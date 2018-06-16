"""
    cloudplayer.api.controller.auth
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import datetime
import hashlib
import urllib

from tornado.log import app_log
import tornado.escape
import tornado.gen
import tornado.httpclient
import tornado.httputil
import tornado.options as opt
import tornado.web

from cloudplayer.api.controller import ControllerException, ProviderRegistry
from cloudplayer.api.model.account import Account
from cloudplayer.api.model.favourite import Favourite
from cloudplayer.api.model.image import Image
from cloudplayer.api.model.provider import Provider

from sqlalchemy.orm.session import make_transient_to_detached


class AuthController(object, metaclass=ProviderRegistry):

    def __init__(self, db, current_user=None, pubsub=None):
        self.db = db
        self.pubsub = pubsub
        self.current_user = current_user
        self.http_client = tornado.httpclient.AsyncHTTPClient()
        self.settings = opt.options[self.__provider__]
        self.account = None
        if current_user:
            id = current_user.get(self.__provider__)
            if id:
                keys = (id, self.__provider__)
                self.account = self.db.query(Account).get(keys)

    @property
    def _should_refresh(self):
        now = datetime.datetime.utcnow()
        return self.account.token_expiration - now < datetime.timedelta(0)

    async def _refresh_access(self):
        body = urllib.parse.urlencode({
            'client_id': self.settings['key'],
            'client_secret': self.settings['secret'],
            'grant_type': 'refresh_token',
            'refresh_token': self.account.refresh_token})

        response = await self._fetch(
            self.OAUTH_ACCESS_TOKEN_URL,
            method='POST', body=body, raise_error=False)
        if response.error:
            message = response.body.decode('utf-8')
            raise ControllerException(403, message)
        access_info = tornado.escape.json_decode(response.body)

        self._update_access_info(access_info)
        self.db.add(self.account)
        self.db.commit()

    async def _fetch(self, request, **kw):
        try:
            response = await self.http_client.fetch(request, **kw)
        except tornado.httpclient.HTTPError as error:
            app_log.warn(error.response.body.decode('utf-8'))
            raise
        return response

    async def fetch(self, path, params=None, **kw):
        if not params:
            params = list()
        elif isinstance(params, dict):
            params = list(params.items())

        if self.account:
            if self._should_refresh:
                await self._refresh_access()

            if self.account.access_token:
                params.append(
                    (self.OAUTH_TOKEN_PARAM, self.account.access_token))
            provider = self.account.provider
        else:
            provider = Provider()
            provider.id = self.__provider__
            make_transient_to_detached(provider)
            provider = self.db.merge(provider, load=False)

        params.append((self.OAUTH_CLIENT_KEY, provider.client_id))

        url = '{}/{}'.format(self.API_BASE_URL, path.lstrip('/'))
        uri = tornado.httputil.url_concat(url, params)
        response = await self._fetch(uri, **kw)
        return response

    def _create_account(self, account_info):
        self.account = Account(
            id=str(account_info['id']),
            user_id=self.current_user['user_id'],
            favourite=Favourite(
                id=str(account_info['id']),
                provider_id=self.__provider__),
            provider_id=self.__provider__)
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
        if not cloudplayer:
            return
        if not cloudplayer.title:
            cloudplayer.title = self.account.title
        if not cloudplayer.image:
            cloudplayer.image = Image(
                small=self.account.image.small,
                medium=self.account.image.medium,
                large=self.account.image.large)

    def update_account(self, access_info, account_info):
        query = self.db.query(Account)
        self.account = query.get((str(account_info['id']), self.__provider__))
        if not self.account:
            self._create_account(account_info)
        self._update_access_info(access_info)
        self._update_account_profile(account_info)
        self._sync_cloudplayer_profile()
        self.db.commit()


class SoundcloudAuthController(AuthController):

    __provider__ = 'soundcloud'
    API_BASE_URL = 'https://api.soundcloud.com'
    OAUTH_ACCESS_TOKEN_URL = 'https://api.soundcloud.com/oauth2/token'
    OAUTH_TOKEN_PARAM = 'oauth_token'
    OAUTH_CLIENT_KEY = 'client_id'

    def _update_account_profile(self, account_info):
        self.account.image = Image.from_soundcloud(
            account_info.get('avatar_url'))
        self.account.title = account_info.get('username')


class YoutubeAuthController(AuthController):

    __provider__ = 'youtube'
    API_BASE_URL = 'https://www.googleapis.com/youtube/v3'
    OAUTH_ACCESS_TOKEN_URL = 'https://www.googleapis.com/oauth2/v4/token'
    OAUTH_TOKEN_PARAM = 'access_token'
    OAUTH_CLIENT_KEY = 'key'

    async def fetch(self, path, params=None, headers=None, **kw):
        if not params:
            params = list()
        elif isinstance(params, dict):
            params = list(params.items())

        params.append(('prettyPrint', 'false'))
        user_hash = hashlib.md5(self.current_user['cloudplayer'].encode())
        params.append(('quotaUser', user_hash.hexdigest()))

        if not headers:
            headers = dict()

        headers['Referer'] = '{}://{}'.format(
            opt.options['public_scheme'], opt.options['public_domain'])

        response = await super().fetch(
            path, params=params, headers=headers, **kw)
        return response

    def _update_account_profile(self, account_info):
        snippet = account_info.get('snippet', {})
        self.account.image = Image.from_youtube(snippet.get('thumbnails'))
        self.account.title = snippet.get('title')

    def update_account(self, access, account_info):
        super().update_account(access, account_info.get('items')[0])
