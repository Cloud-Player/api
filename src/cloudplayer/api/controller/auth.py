"""
    cloudplayer.api.controller.auth
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
import datetime
import urllib

import tornado.options as opt
import tornado.httpclient
import tornado.httputil
import tornado.escape
import tornado.gen
import tornado.web

from cloudplayer.api.model.account import Account
from cloudplayer.api.model.image import Image


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
        id = (current_user or {}).get(self.PROVIDER_ID)
        if id:
            self.account = self.db.query(Account).get((id, self.PROVIDER_ID))
        else:
            self.account = None

    @property
    def should_refresh(self):
        now = datetime.datetime.utcnow()
        return self.account.token_expiration - now < datetime.timedelta(0)

    @tornado.gen.coroutine
    def refresh(self):
        body = urllib.parse.urlencode({
            'client_id': self.settings['key'],
            'client_secret': self.settings['secret'],
            'refresh_token': self.account.refresh_token,
            'grant_type': 'refresh_token'
        })
        uri = self.OAUTH_ACCESS_TOKEN_URL
        response = yield self.http_client.fetch(
            uri, method='POST', body=body, raise_error=False)

        if response.error:
            self.account.access_token = None
            self.account.refresh_token = None
            self.account.token_expiration = datetime.datetime.utcnow()
        else:
            access = tornado.escape.json_decode(response.body)
            self.account.access_token = access.get('access_token')
            if access.get('refresh_token'):
                self.account.refresh_token = access['refresh_token']
            if access.get('expires_in'):
                expires_in = datetime.timedelta(
                    seconds=access.get('expires_in'))
                self.account.token_expiration = (
                    datetime.datetime.utcnow() + expires_in)

        self.db.add(self.account)
        self.db.commit()

    @tornado.gen.coroutine
    def fetch(self, path, params=None, **kw):
        if not params:
            params = list()
        elif isinstance(params, dict):
            params = list(params.items())

        if self.account:
            if self.should_refresh:
                yield self.refresh()

            if self.account.access_token:
                params.append(
                    (self.OAUTH_TOKEN_PARAM, self.account.access_token))
            provider = self.account.provider
        else:
            from cloudplayer.api.model.provider import Provider
            provider = self.db.query(Provider).get(self.PROVIDER_ID)

        params.append((self.OAUTH_CLIENT_KEY, provider.client_id))

        url = '{}/{}'.format(self.API_BASE_URL, path.lstrip('/'))
        uri = tornado.httputil.url_concat(url, params)
        response = yield self.http_client.fetch(uri, **kw)
        return response

    def _create_account(self, user_info):
        self.account = Account(
            id=str(user_info['id']),
            user_id=self.current_user['user_id'],
            provider_id=self.PROVIDER_ID)
        self.db.add(self.account)

    def _update_account_profile(self, user_info):
        pass

    def _update_cloudplayer_profile(self, user_info):
        cloudplayer = self.db.query(Account).get((
            self.current_user['cloudplayer'], 'cloudplayer'))
        if not cloudplayer.title:
            cloudplayer.title = self.account.title
        if not cloudplayer.image:
            cloudplayer.image = self.account.image

    def update_account(self, user_info):
        self.account = self.db.query(
            Account).get((str(user_info['id']), self.PROVIDER_ID))
        if not self.account:
            self._create_account(user_info)
        self._update_account_profile(user_info)
        self._update_cloudplayer_profile(user_info)
        self.db.commit()


class SoundcloudAuthController(AuthController):

    PROVIDER_ID = 'soundcloud'
    API_BASE_URL = 'https://api.soundcloud.com'
    OAUTH_ACCESS_TOKEN_URL = 'https://api.soundcloud.com/oauth2/token'
    OAUTH_TOKEN_PARAM = 'oauth_token'
    OAUTH_CLIENT_KEY = 'client_id'

    def _update_account_profile(self, user_info):
        image_url = user_info.get('avatar_url')
        self.account.image = Image(
            small=image_url,
            medium=image_url.replace('large', 't300x300'),
            large=image_url.replace('large', 't500x500'))
        self.account.title = user_info.get('username')

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
        params.append(('quotaUser', self.current_user[self.PROVIDER_ID]))

        if not headers:
            headers = dict()
        headers['Referer'] = 'https://api.cloud-player.io'

        response = yield super().fetch(path, params, headers=headers, **kw)
        return response

    def _update_account_profile(self, user_info):
        snippet = user_info.get('snippet', {})
        thumbnails = snippet.get('thumbnails', {})
        self.account.image = Image(
            small=thumbnails.get('default', {}).get('url'),
            medium=thumbnails.get('medium', {}).get('url'),
            large=thumbnails.get('high', {}).get('url'))
        self.account.title = snippet.get('title')

    def update_account(self, user_info):
        super().update_account(user_info.get('items')[0])
