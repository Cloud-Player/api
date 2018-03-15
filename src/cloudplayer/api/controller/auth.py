"""
    cloudplayer.api.controller.auth
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import datetime
import hashlib
import urllib

import tornado.escape
import tornado.gen
import tornado.httpclient
import tornado.httputil
import tornado.options as opt
import tornado.web

from cloudplayer.api.controller import ControllerException
from cloudplayer.api.model.account import Account
from cloudplayer.api.model.image import Image
from cloudplayer.api.model.provider import Provider

from sqlalchemy.orm.session import make_transient_to_detached


def create_controller(provider_id, db, current_user=None):
    if provider_id == 'soundcloud':
        return SoundcloudAuthController(db, current_user)
    elif provider_id == 'youtube':
        return YoutubeAuthController(db, current_user)
    else:
        raise ValueError('unsupported provider')


class AuthController(object):

    def __init__(self, db, current_user=None):
        self.db = db
        self.current_user = current_user
        self.http_client = tornado.httpclient.AsyncHTTPClient()
        self.settings = opt.options[self.PROVIDER_ID]
        self.account = None
        if current_user:
            id = current_user.get(self.PROVIDER_ID)
            if id:
                keys = (id, self.PROVIDER_ID)
                self.account = self.db.query(Account).get(keys)

    @property
    def _should_refresh(self):
        now = datetime.datetime.utcnow()
        return self.account.token_expiration - now < datetime.timedelta(0)

    @tornado.gen.coroutine
    def _refresh_access(self):
        body = urllib.parse.urlencode({
            'client_id': self.settings['key'],
            'client_secret': self.settings['secret'],
            'grant_type': 'refresh_token',
            'refresh_token': self.account.refresh_token})

        response = yield self.http_client.fetch(
            self.OAUTH_ACCESS_TOKEN_URL,
            method='POST', body=body, raise_error=False)
        if response.error:
            raise ControllerException(403, 'refresh failed')
        access_info = tornado.escape.json_decode(response.body)

        self._update_access_info(access_info)
        self.db.add(self.account)
        self.db.commit()

    @tornado.gen.coroutine
    def fetch(self, path, params=None, **kw):
        if not params:
            params = list()
        elif isinstance(params, dict):
            params = list(params.items())

        if self.account:
            if self._should_refresh:
                yield self._refresh_access()

            if self.account.access_token:
                params.append(
                    (self.OAUTH_TOKEN_PARAM, self.account.access_token))
            provider = self.account.provider
        else:
            provider = Provider()
            provider.id = self.PROVIDER_ID
            make_transient_to_detached(provider)
            provider = self.db.merge(provider, load=False)

        params.append((self.OAUTH_CLIENT_KEY, provider.client_id))

        url = '{}/{}'.format(self.API_BASE_URL, path.lstrip('/'))
        uri = tornado.httputil.url_concat(url, params)
        response = yield self.http_client.fetch(uri, **kw)
        return response

    def _create_account(self, account_info):
        self.account = Account(
            id=str(account_info['id']),
            user_id=self.current_user['user_id'],
            provider_id=self.PROVIDER_ID)
        self.db.add(self.account)

    def _update_access_info(self, access_info):
        if access_info.get('access_token'):
            self.account.access_token = access_info['access_token']
        if access_info.get('refresh_token'):
            self.account.refresh_token = access_info['refresh_token']
        if access_info.get('expires_in'):
            self.account.token_expiration = datetime.datetime.utcnow() + (
                datetime.timedelta(seconds=access_info['expires_in']))

    def _update_account_profile(self, account_info):
        raise NotImplementedError()  # pragma: no cover

    def _sync_cloudplayer_profile(self):
        cloudplayer = self.db.query(Account).get((
            self.current_user['cloudplayer'], 'cloudplayer'))
        if not cloudplayer.title:
            cloudplayer.title = self.account.title
        if not cloudplayer.image:
            cloudplayer.image = self.account.image

    def update_account(self, access_info, account_info):
        query = self.db.query(Account)
        self.account = query.get((str(account_info['id']), self.PROVIDER_ID))
        if not self.account:
            self._create_account(account_info)
        self._update_access_info(access_info)
        self._update_account_profile(account_info)
        self._sync_cloudplayer_profile()
        self.db.commit()


class SoundcloudAuthController(AuthController):

    PROVIDER_ID = 'soundcloud'
    API_BASE_URL = 'https://api.soundcloud.com'
    OAUTH_ACCESS_TOKEN_URL = 'https://api.soundcloud.com/oauth2/token'
    OAUTH_TOKEN_PARAM = 'oauth_token'
    OAUTH_CLIENT_KEY = 'client_id'

    def _update_account_profile(self, account_info):
        image_url = account_info.get('avatar_url')
        self.account.image = Image(
            small=image_url,
            medium=image_url.replace('large', 't300x300'),
            large=image_url.replace('large', 't500x500'))
        self.account.title = account_info.get('username')


class YoutubeAuthController(AuthController):

    PROVIDER_ID = 'youtube'
    API_BASE_URL = 'https://www.googleapis.com/youtube/v3'
    OAUTH_ACCESS_TOKEN_URL = 'https://www.googleapis.com/oauth2/v4/token'
    OAUTH_TOKEN_PARAM = 'access_token'
    OAUTH_CLIENT_KEY = 'key'

    @tornado.gen.coroutine
    def fetch(self, path, params=None, headers=None, **kw):
        if not params:
            params = list()
        elif isinstance(params, dict):
            params = list(params.items())

        params.append(('prettyPrint', 'false'))
        user_hash = hashlib.md5(self.current_user['cloudplayer'].encode())
        params.append(('quotaUser', user_hash.hexdigest()))

        if not headers:
            headers = dict()
        headers['Referer'] = 'https://api.cloud-player.io'

        response = yield super().fetch(
            path, params=params, headers=headers, **kw)
        return response

    def _update_account_profile(self, account_info):
        snippet = account_info.get('snippet', {})
        thumbnails = snippet.get('thumbnails', {})
        self.account.image = Image(
            small=thumbnails.get('default', {}).get('url'),
            medium=thumbnails.get('medium', {}).get('url'),
            large=thumbnails.get('high', {}).get('url'))
        self.account.title = snippet.get('title')

    def update_account(self, access, account_info):
        super().update_account(access, account_info.get('items')[0])
