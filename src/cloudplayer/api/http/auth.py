"""
    cloudplayer.api.http.auth
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
import functools
import datetime
import traceback

import tornado.auth
import tornado.web
import tornado.escape

from cloudplayer.api.model.account import Account
from cloudplayer.api.model.image import Image
from cloudplayer.api.http import HTTPHandler


class AuthHandler(HTTPHandler, tornado.auth.OAuth2Mixin):

    _OAUTH_NO_CALLBACKS = False
    _OAUTH_VERSION = '1.0a'
    _OAUTH_RESPONSE_TYPE = 'code'
    _OAUTH_GRANT_TYPE = 'authorization_code'

    _OAUTH_SCOPE_LIST = []
    _OAUTH_EXTRA_PARAMS = {}

    _OAUTH_AUTHORIZE_URL = NotImplemented
    _OAUTH_ACCESS_TOKEN_URL = NotImplemented
    _OAUTH_USERINFO_URL = NotImplemented
    _OAUTH_SETTINGS_KEY = NotImplemented
    _OAUTH_PROVIDER_ID = NotImplemented

    @property
    def _OAUTH_PROVIDER(self):
        return self.settings[self._OAUTH_SETTINGS_KEY]

    @tornado.auth._auth_return_future
    def get_authenticated_user(self, redirect_uri, code, callback):
        """Fetches the authenticated user data upon redirect"""
        http = self.get_auth_http_client()
        body = tornado.auth.urllib_parse.urlencode({
            'redirect_uri': redirect_uri,
            'code': code,
            'client_id': self._OAUTH_PROVIDER['key'],
            'client_secret': self._OAUTH_PROVIDER['secret'],
            'grant_type': self._OAUTH_GRANT_TYPE})

        http.fetch(
            self._OAUTH_ACCESS_TOKEN_URL,
            functools.partial(self._on_access_token, callback),
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            method='POST',
            body=body)

    def _on_access_token(self, future, response):
        """Callback function for the exchange to the access token"""
        if response.error:
            future.set_exception(
                tornado.auth.AuthError('{} auth error: {}'.format(
                    self._OAUTH_PROVIDER_ID, response)))
        else:
            args = tornado.escape.json_decode(response.body)
            future.set_result(args)

    @tornado.gen.coroutine
    def get(self):
        if self.get_argument('code', None) is not None:
            try:
                yield self.provider_callback()
            except:
                traceback.print_exc()
            finally:
                self.redirect('/static/close.html')
        else:
            yield self.authorize_redirect(
                redirect_uri=self._OAUTH_PROVIDER['redirect_uri'],
                client_id=self._OAUTH_PROVIDER['key'],
                scope=self._OAUTH_SCOPE_LIST,
                response_type=self._OAUTH_RESPONSE_TYPE,
                extra_params=self._OAUTH_EXTRA_PARAMS)

    @tornado.gen.coroutine
    def provider_callback(self):
        access = yield self.get_authenticated_user(
            redirect_uri=self._OAUTH_PROVIDER['redirect_uri'],
            code=self.get_argument('code'))

        args = {'access_token': True}
        args[self.OAUTH_TOKEN_PARAM] = access.get('access_token')
        user_info = yield self.oauth2_request(
            self._OAUTH_USERINFO_URL, **args)

        if not user_info:
            raise tornado.web.HTTPError(503, 'invalid user info')

        account = self.db.query(Account).get((
            str(user_info['id']), self._OAUTH_PROVIDER_ID))

        if account:
            self.current_user['user_id'] = account.user_id
            for a in account.user.accounts:
                self.current_user[a.provider_id] = a.id
        else:
            expires_in = datetime.timedelta(seconds=access.get('expires_in'))
            # TODO: Move image url parsing to concrete auth classes
            if self._OAUTH_PROVIDER_ID == 'soundcloud':
                image_url = user_info.get('avatar_url')
                image = Image(
                    small=image_url,
                    medium=image_url.replace('large', 't300x300'),
                    large=image_url.replace('large', 't500x500')
                )
            elif self._OAUTH_PROVIDER_ID == 'youtube':
                image_url = user_info.get('picture')
                image = Image(
                    small=image_url.replace('/photo.jpg', '/s100/photo.jpg'),
                    medium=image_url.replace('/photo.jpg', '/s300/photo.jpg'),
                    large=image_url.replace('/photo.jpg', '/s500/photo.jpg'),
                )
            else:
                image = None
            account = Account(
                id=str(user_info['id']),
                image=image,
                title=(
                    user_info.get('name') or
                    user_info.get('full_name') or
                    user_info.get('username')),
                user_id=self.current_user['user_id'],
                provider_id=self._OAUTH_PROVIDER_ID,
                access_token=access.get('access_token'),
                refresh_token=access.get('refresh_token'),
                token_expiration=datetime.datetime.now() + expires_in)
            self.db.add(account)
            self.current_user[self._OAUTH_PROVIDER_ID] = account.id

            cloudplayer = self.db.query(Account).get((
                self.current_user['cloudplayer'], 'cloudplayer'))

            if cloudplayer:
                if not cloudplayer.title:
                    cloudplayer.title = account.title
                if not cloudplayer.image:
                    cloudplayer.image = account.image

            self.db.commit()

        self.set_user_cookie()


class Soundcloud(AuthHandler):

    API_BASE_URL = 'https://api.soundcloud.com'
    OAUTH_TOKEN_PARAM = 'oauth_token'

    _OAUTH_AUTHORIZE_URL = 'https://soundcloud.com/connect'
    _OAUTH_ACCESS_TOKEN_URL = 'https://api.soundcloud.com/oauth2/token'
    _OAUTH_USERINFO_URL = 'https://api.soundcloud.com/me'
    _OAUTH_SETTINGS_KEY = 'soundcloud_oauth'
    _OAUTH_PROVIDER_ID = 'soundcloud'
    _OAUTH_CLIENT_KEY = 'client_id'
    _OAUTH_SCOPE_LIST = []

    @property
    def _OAUTH_EXTRA_PARAMS(self):
        return {'state': self.settings['menuflow_state']}


class Youtube(AuthHandler):

    API_BASE_URL = 'https://www.googleapis.com/youtube/v3'
    OAUTH_TOKEN_PARAM = 'access_token'

    _OAUTH_AUTHORIZE_URL = 'https://accounts.google.com/o/oauth2/auth'
    _OAUTH_ACCESS_TOKEN_URL = 'https://www.googleapis.com/oauth2/v4/token'
    _OAUTH_USERINFO_URL = 'https://www.googleapis.com/oauth2/v1/userinfo'
    # TODO: get user info from youtube/channels?mine=true&part=snippet
    _OAUTH_SETTINGS_KEY = 'youtube_oauth'
    _OAUTH_PROVIDER_ID = 'youtube'
    _OAUTH_CLIENT_KEY = 'key'
    _OAUTH_SCOPE_LIST = [
        'profile', 'email', 'https://www.googleapis.com/auth/youtube']
    _OAUTH_EXTRA_PARAMS = {
        'approval_prompt': 'auto', 'access_type': 'offline'}
