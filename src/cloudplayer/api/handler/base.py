"""
    cloudplayer.api.handler
    ~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
import datetime
import json
import urllib

import jwt
import jwt.exceptions
import redis
import tornado.auth
import tornado.escape
import tornado.gen
import tornado.httputil
import tornado.options as opt
import tornado.web

from cloudplayer.api.model import Encoder
from cloudplayer.api.model.account import Account
from cloudplayer.api.model.user import User


class HTTPHandler(tornado.web.RequestHandler):

    SUPPORTED_METHODS = ('GET', 'POST', 'DELETE', 'PUT', 'OPTIONS')

    def __init__(self, request, application):
        super().__init__(request, application)
        self.http_client = tornado.httpclient.AsyncHTTPClient()
        self.database_session = None
        self._current_user = None
        self._original_user = None

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
            user = jwt.decode(
                self.get_cookie(self.settings['jwt_cookie'], ''),
                self.settings['jwt_secret'],
                algorithms=['HS256'])
            self._original_user = user
        except jwt.exceptions.InvalidTokenError:
            new_user = User()
            self.db.add(new_user)
            self.db.commit()
            new_account = Account(
                id=str(new_user.id),
                provider_id='cloudplayer',
                user_id=new_user.id)
            self.db.add(new_account)
            self.db.commit()
            user = {p: None for p in self.settings['providers']}
            user['cloudplayer'] = new_account.id
            user['user_id'] = new_user.id
        return user

    def set_user_cookie(self):
        user_jwt = jwt.encode(
            self._current_user,
            self.settings['jwt_secret'],
            algorithm='HS256')
        super().set_cookie(
            self.settings['jwt_cookie'],
            user_jwt,
            expires_days=self.settings['jwt_expiration'])

    @property
    def current_user(self):
        if self._current_user is None:
            self._current_user = self.get_current_user()
        return self._current_user

    @current_user.setter
    def current_user(self, user):
        self._current_user = user

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

    def finish(self, chunk=None):
        if self._original_user != self._current_user:
            self.set_user_cookie()
        self.db.close()
        super().finish(chunk=chunk)

    @tornado.gen.coroutine
    def fetch(self, provider_id, path, params=[], **kw):
        import cloudplayer.api.handler.auth
        if provider_id == 'youtube':
            auth_class = cloudplayer.api.handler.auth.Youtube
        elif provider_id == 'soundcloud':
            auth_class = cloudplayer.api.handler.auth.Soundcloud
        else:
            raise ValueError('unsupported provider')
        url = '{}/{}'.format(auth_class.API_BASE_URL, path.lstrip('/'))

        account = self.db.query(Account).get((
            self.current_user[provider_id], provider_id))

        if account:
            # TODO: Move refresh workflow to auth module
            settings = self.settings[auth_class._OAUTH_SETTINGS_KEY]
            tzinfo = account.token_expiration.tzinfo
            now = datetime.datetime.now(tzinfo)
            threshold = datetime.timedelta(minutes=1)
            if account.token_expiration - now < threshold:
                body = urllib.parse.urlencode({
                    'client_id': settings['key'],
                    'client_secret': settings['secret'],
                    'refresh_token': account.refresh_token,
                    'grant_type': 'refresh_token'
                })
                uri = auth_class._OAUTH_ACCESS_TOKEN_URL
                response = yield self.http_client.fetch(
                    uri, method='POST', body=body, raise_error=False)
                access = json.load(response.buffer)
                account.access_token = access.get('access_token')
                expires_in = datetime.timedelta(
                    seconds=access.get('expires_in'))
                account.token_expiration = (
                    datetime.datetime.now(tzinfo) + expires_in)
                self.db.commit()

            params.append((auth_class.OAUTH_TOKEN_PARAM, account.access_token))
            params.append((auth_class._OAUTH_CLIENT_KEY, settings['api_key']))

        uri = tornado.httputil.url_concat(url, params)

        headers = kw.get('headers', {})
        headers['Referer'] = 'https://api.cloud-player.io'
        kw['headers'] = headers

        response = yield self.http_client.fetch(uri, **kw)
        return response

    @property
    def body_json(self):
        try:
            return json.loads(self.request.body)
        except ValueError as error:
            raise tornado.web.HTTPError(400, error.message)

    @property
    def query_params(self):
        params = []
        for name, vals in self.request.query_arguments.items():
            for v in vals:
                params.append((name, v.decode('utf-8')))
        return params

    @tornado.gen.coroutine
    def options(self, *args, **kw):
        self.finish()

    @property
    def allowed_origin(self):
        proposed_origin = self.request.headers.get('Origin')
        if proposed_origin in self.settings['allowed_origins']:
            return proposed_origin
        return self.settings['allowed_origins'][0]

    @property
    def allowed_methods(self):
        return ', '.join(list(self.SUPPORTED_METHODS) + ['OPTIONS'])


class ControllerHandler(HTTPHandler):

    __controller__ = NotImplemented

    def __init__(self, request, application):
        super().__init__(request, application)
        self.controller = self.__controller__(self.db, self.current_user)


class EntityHandler(ControllerHandler):

    SUPPORTED_METHODS = ['GET', 'PATCH', 'DELETE']

    @tornado.gen.coroutine
    def get(self, **ids):
        entity = self.controller.read(ids)
        yield self.write(entity)

    @tornado.gen.coroutine
    def patch(self, **ids):
        entity = self.controller.update(ids, **self.body_json)
        yield self.write(entity)

    @tornado.gen.coroutine
    def delete(self, **ids):
        entity = self.controller.delete(ids)
        self.set_status(204)
        self.finish()


class CollectionHandler(ControllerHandler):

    SUPPORTED_METHODS = ['GET', 'POST']

    @tornado.gen.coroutine
    def get(self, **ids):
        query = dict(self.query_params)
        entities = self.controller.search(ids, **query)
        yield self.write(entities)

    @tornado.gen.coroutine
    def post(self, **ids):
        entity = self.controller.create(ids, **self.body_json)
        yield self.write(entity)


class FallbackHandler(HTTPHandler):

    def get(self, *args, **kwargs):
        self.send_error(404, reason='resource not found')
