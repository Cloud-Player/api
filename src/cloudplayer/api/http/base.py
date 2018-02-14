"""
    cloudplayer.api.http.base
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import json

import jwt
import jwt.exceptions
import tornado.auth
import tornado.escape
import tornado.gen
import tornado.httputil
import tornado.web

from cloudplayer.api import APIException
from cloudplayer.api.handler import HandlerMixin
from cloudplayer.api.model import Encoder
from cloudplayer.api.model.account import Account
from cloudplayer.api.model.favourite import Favourite
from cloudplayer.api.model.user import User


class HTTPException(APIException):
    pass


class HTTPHandler(HandlerMixin, tornado.web.RequestHandler):

    SUPPORTED_METHODS = ('GET', 'POST', 'PATCH', 'DELETE', 'OPTIONS')

    def __init__(self, request, application):
        super().__init__(request, application)
        self.current_user = None
        self.original_user = None

    def load_user(self):
        try:
            user = jwt.decode(
                self.get_cookie(self.settings['jwt_cookie'], ''),
                self.settings['jwt_secret'],
                algorithms=['HS256'])
            return user, user.copy()
        except jwt.exceptions.InvalidTokenError:
            new_user = User()
            self.db.add(new_user)
            self.db.commit()
            new_account = Account(
                id=str(new_user.id),
                provider_id='cloudplayer',
                favourite=Favourite(),
                user_id=new_user.id)
            self.db.add(new_account)
            self.db.commit()
            user = {p: None for p in self.settings['providers']}
            user['cloudplayer'] = new_account.id
            user['user_id'] = new_user.id
            return None, user

    def prepare(self):
        self.original_user, self.current_user = self.load_user()

    def set_user_cookie(self):
        user_jwt = jwt.encode(
            self.current_user,
            self.settings['jwt_secret'],
            algorithm='HS256')
        super().set_cookie(
            self.settings['jwt_cookie'],
            user_jwt,
            expires_days=self.settings['jwt_expiration'])

    def clear_user_cookie(self):
        super().clear_cookie(self.settings['jwt_cookie'])

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
            raise HTTPException(404)
        json.dump(data, super(), cls=Encoder)
        self.finish()

    def finish(self, chunk=None):
        if self.original_user != self.current_user:
            self.set_user_cookie()
        elif not self.current_user:
            self.clear_user_cookie()
        super().finish(chunk=chunk)

    @property
    def body(self):
        if not self.request.body:
            return {}
        try:
            return tornado.escape.json_decode(self.request.body)
        except (json.decoder.JSONDecodeError, ValueError):
            raise HTTPException(400, 'invalid json body')

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
        return ', '.join(self.SUPPORTED_METHODS)


class HTTPFallback(HTTPHandler):

    SUPPORTED_METHODS = ('GET',)

    def get(self, *args, **kwargs):
        raise HTTPException(404)


class HTTPHealth(HTTPHandler):

    SUPPORTED_METHODS = ('GET',)

    def get(self, *args, **kwargs):
        self.cache.info()
        self.db.execute('SELECT 1 = 1;').first()
        self.write({'status_code': 200, 'reason': 'OK'})
