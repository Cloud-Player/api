"""
    cloudplayer.api.http.auth
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import datetime
import functools
import traceback

import tornado.auth
import tornado.escape
import tornado.httputil
import tornado.options as opt
import tornado.web

from cloudplayer.api.http import HTTPException
from cloudplayer.api.controller.auth import SoundcloudAuthController
from cloudplayer.api.controller.auth import YoutubeAuthController
from cloudplayer.api.handler import ControllerHandlerMixin
from cloudplayer.api.http import HTTPHandler


class AuthHandler(
        ControllerHandlerMixin, HTTPHandler, tornado.auth.OAuth2Mixin):

    _OAUTH_NO_CALLBACKS = False
    _OAUTH_VERSION = '1.0a'
    _OAUTH_RESPONSE_TYPE = 'code'
    _OAUTH_GRANT_TYPE = 'authorization_code'

    _OAUTH_SCOPE_LIST = []
    _OAUTH_EXTRA_PARAMS = {}

    _OAUTH_AUTHORIZE_URL = NotImplemented
    _OAUTH_USERINFO_URL = NotImplemented

    @property
    def _OAUTH_CLIENT_ID(self):
        return opt.options[self.PROVIDER_ID]['key']

    @property
    def _OAUTH_CLIENT_SECRET(self):
        return opt.options[self.PROVIDER_ID]['secret']

    @property
    def _OAUTH_REDIRECT_URI(self):
        return opt.options[self.PROVIDER_ID]['redirect_uri']

    @tornado.auth._auth_return_future
    def get_authenticated_user(self, redirect_uri, code, callback):
        """Fetches the authenticated user data upon redirect"""
        http = self.get_auth_http_client()
        body = tornado.auth.urllib_parse.urlencode({
            'redirect_uri': redirect_uri,
            'code': code,
            'client_id': self._OAUTH_CLIENT_ID,
            'client_secret': self._OAUTH_CLIENT_SECRET,
            'grant_type': self._OAUTH_GRANT_TYPE})

        http.fetch(
            self.controller.OAUTH_ACCESS_TOKEN_URL,
            functools.partial(self._on_access_token, callback),
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            method='POST',
            body=body)

    def _on_access_token(self, future, response):
        """Callback function for the exchange to the access token"""
        if response.error:
            future.set_exception(
                tornado.auth.AuthError('{} auth error: {}'.format(
                    self.PROVIDER_ID, response)))
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
                redirect_uri=self._OAUTH_REDIRECT_URI,
                client_id=self._OAUTH_CLIENT_ID,
                scope=self._OAUTH_SCOPE_LIST,
                response_type=self._OAUTH_RESPONSE_TYPE,
                extra_params=self._OAUTH_EXTRA_PARAMS)

    @tornado.gen.coroutine
    def provider_callback(self):
        # exchange oauth code for access_token
        access = yield self.get_authenticated_user(
            redirect_uri=self._OAUTH_REDIRECT_URI,
            code=self.get_argument('code'))

        # retrieve user_info using access_token
        uri = tornado.httputil.url_concat(
            self._OAUTH_USERINFO_URL,
            {'access_token': True,
             self.controller.OAUTH_TOKEN_PARAM: access.get('access_token')})
        user_info = yield self.oauth2_request(uri)
        if not user_info:
            raise HTTPException(503, 'invalid user info')

        # update or create a new account for this provider
        self.controller.update_account(user_info)
        account = self.controller.account

        # sync user account info back to cookie
        self.current_user['user_id'] = account.user_id
        for p in opt.options['providers']:
            self.current_user[p] = None
        for a in account.user.accounts:
            self.current_user[a.provider_id] = a.id
        self.set_user_cookie()

        # attach new token combo to account model
        account.access_token = access['access_token']
        if access.get('refresh_token'):
            account.refresh_token = access['refresh_token']
            account.token_expiration = datetime.datetime.utcnow() + (
                datetime.timedelta(seconds=access.get('expires_in')))
        self.db.commit()


class Soundcloud(AuthHandler):

    __controller__ = SoundcloudAuthController

    PROVIDER_ID = 'soundcloud'
    _OAUTH_AUTHORIZE_URL = 'https://soundcloud.com/connect'
    _OAUTH_USERINFO_URL = 'https://api.soundcloud.com/me'
    _OAUTH_SCOPE_LIST = []

    @property
    def _OAUTH_EXTRA_PARAMS(self):
        return {'state': self.settings['menuflow_state']}


class Youtube(AuthHandler):

    __controller__ = YoutubeAuthController

    PROVIDER_ID = 'youtube'
    _OAUTH_AUTHORIZE_URL = 'https://accounts.google.com/o/oauth2/auth'
    _OAUTH_USERINFO_URL = ('https://www.googleapis.com/youtube/v3/channels'
                           '?part=snippet&mine=true')
    _OAUTH_SCOPE_LIST = [
        'profile', 'email', 'https://www.googleapis.com/auth/youtube']
    _OAUTH_EXTRA_PARAMS = {
        'approval_prompt': 'auto', 'access_type': 'offline'}
