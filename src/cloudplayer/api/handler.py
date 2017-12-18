"""
    cloudplayer.api.handler
    ~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
import datetime
import functools
import json
import traceback

from sqlalchemy.orm.session import make_transient_to_detached
import jwt
import jwt.exceptions
import tornado.auth
import tornado.escape
import tornado.gen
import tornado.httputil
import tornado.options as opt
import tornado.web

from cloudplayer.api.model import Account, User, Provider, Encoder
import cloudplayer.api.auth


class HTTPHandler(tornado.web.RequestHandler):

    SUPPORTED_METHODS = ('GET', 'POST', 'DELETE', 'PUT', 'OPTIONS')

    def __init__(self, request, application):
        super(HTTPHandler, self).__init__(request, application)
        self.http_client = tornado.httpclient.AsyncHTTPClient()
        self.database_session = None
        self._current_user = None

    @property
    def cache(self):
        return redis.Redis(connection_pool=self.application.redis_pool)

    @property
    def db(self):
        if not self.database_session:
            self.database_session = self.application.database.create_session()
        return self.database_session

    def get_current_user(self):
        try:
            return jwt.decode(
                self.get_cookie(self.settings['jwt_cookie'], ''),
                self.settings['jwt_secret'],
                algorithms=['HS256'])
        except jwt.exceptions.InvalidTokenError:
            user = User()
            self.db.add(user)
            self.db.commit()
            claim = {p: None for p in self.settings['providers']}
            claim['cloudplayer'] = user.id
            return claim

    @property
    def current_user(self):
        if self._current_user is None:
            self.current_user = self.get_current_user()
        return self._current_user

    @current_user.setter
    def current_user(self, value):
        if self._current_user != value:
            user_jwt = jwt.encode(
                value,
                self.settings['jwt_secret'],
                algorithm='HS256')
            super().set_cookie(
                self.settings['jwt_cookie'],
                user_jwt,
                expires_days=self.settings['jwt_expiration'])
        self._current_user = value

    def set_default_headers(self):
        headers = [
            ('Access-Control-Allow-Credentials', 'true'),
            ('Access-Control-Allow-Headers', 'Accept, Content-Type, Origin'),
            ('Access-Control-Allow-Methods', self.allowed_methods),
            ('Access-Control-Allow-Origin', self.allowed_origin),
            ('Access-Control-Max-Age', '600'),
            ('Cache-Control', 'no-cache, no-store, must-revalidate'),
            ('Content-Language', 'en-US'),
            ('Content-Type', 'application/json'),
            ('Pragma', 'no-cache'),
            ('Server', 'cloudplayer')
        ]
        for header, value in headers:
            self.set_header(header, value)

    def write(self, data):
        if data is None:
            raise tornado.web.HTTPError(404, 'not found')
        json.dump(data, super(HTTPHandler, self), cls=Encoder)
        self.finish()

    def write_error(self, status_code, **kw):
        reason = 'no reason given'
        if 'reason' in kw:
            reason = kw['reason']
        elif 'exc_info' in kw:
            exception = kw['exc_info'][1]
            for attr in ('reason', 'message', 'log_message'):
                if getattr(exception, attr, None):
                    reason = getattr(exception, attr)
                    break
        self.write({'status_code': status_code, 'reason': reason})

    def fetch(self, provider, path, params={}, **kw):
        if provider == 'youtube':
            auth_class = auth.Youtube
        elif provider == 'soundcloud':
            auth_class = auth.Soundcloud
        url = '{}/{}'.format(auth_class.API_BASE_URL, path)
        params[auth_class.OAUTH_TOKEN_PARAM] = self.current_user[provider]
        uri = tornado.httputil.url_concat(url, params)
        return self.http_client.fetch(uri)

    def body_json(self):
        try:
            return json.loads(self.request.body)
        except ValueError as error:
            raise tornado.web.HTTPError(400, error.message)

    @tornado.gen.coroutine
    def options(self, *args, **kwargs):
        self.finish()

    @property
    def allowed_origin(self):
        proposed_origin = self.request.headers.get('Origin')
        if proposed_origin in self.settings['allowed_origins']:
            return proposed_origin
        return self.settings['allowed_origins'][0]

    @property
    def allowed_methods(self):
        return ', '.join(self.SUPPORTED_METHODS)


class EntityHandler(HTTPHandler):

    __model__ = NotImplemented

    SUPPORTED_METHODS = ['GET', 'PUT', 'PATCH', 'DELETE']

    @classmethod
    def update(entity, dict_):
        for field, value in dict_.items():
            if field in entity.__fields__:
                setattr(entity, field, value)
            else:
                raise KeyError('invalid field %s' % field)

    @tornado.gen.coroutine
    def get(self, id):
        entity = self.db.query(
            self.__model__
        ).filter(
            self.__model__.id == id
        ).one_or_none()

        yield self.write(entity)

    @tornado.gen.coroutine
    def put(self, id):
        entity = self.db.query(
            self.__model__
        ).filter(
            self.__model__.id == id
        ).one_or_none()

        if entity is None:
            raise tornado.web.HTTPError(404, 'entity not found')

        self.update(entity, body_json)

        self.db.commit()

        yield self.write(entity)


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

        user_info = yield self.oauth2_request(
            self._OAUTH_USERINFO_URL,
            access_token=True,
            **{self.OAUTH_TOKEN_PARAM: access['access_token']})

        account = self.db.query(
            Account
        ).filter(
            Account.id == str(user_info['id'])
        ).filter(
            Account.provider_id == self._OAUTH_PROVIDER_ID
        ).one_or_none()

        if not account:
            expires_in = datetime.timedelta(seconds=access['expires_in'])
            account = Account(
                id=str(user_info['id']),
                user_id=self.current_user[self._OAUTH_PROVIDER_ID],
                provider_id=self._OAUTH_PROVIDER_ID,
                access_token=access['access_token'],
                refresh_token=access['refresh_token'],
                token_expiration=datetime.datetime.now() + expires_in)
            self.db.add(account)

        # TODO: -re-assign to user/accounts
        self.db.commit()


class FallbackHandler(HTTPHandler):

    def get(self, *args, **kwargs):
        self.send_error(404, reason='resource not found')
