"""
    cloudplayer.api.http.base
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
import json
import datetime
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

from cloudplayer.api.handler import HandlerMixin
from cloudplayer.api.model import Encoder
from cloudplayer.api.model.account import Account
from cloudplayer.api.model.user import User


class HTTPHandler(HandlerMixin, tornado.web.RequestHandler):

    SUPPORTED_METHODS = ('GET', 'POST', 'PATCH', 'DELETE', 'OPTIONS')

    def __init__(self, request, application):
        super().__init__(request, application)
        self._current_user = None
        self._original_user = None

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
        json.dump(data, super(), cls=Encoder)
        self.finish()

    def finish(self, chunk=None):
        if self._original_user != self._current_user:
            self.set_user_cookie()
        super().finish(chunk=chunk)

    @property
    def body(self):
        try:
            return tornado.escape.json_decode(self.request.body)
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
        return ', '.join(self.SUPPORTED_METHODS)


class HTTPFallback(HTTPHandler):

    def get(self, *args, **kwargs):
        self.write_error(404, reason='resource not found')
