"""
    cloudplayer.api.handler
    ~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: Apache-2.0, see LICENSE for details
"""
import json

import jwt
import jwt.exceptions

from sqlalchemy.orm.session import make_transient_to_detached
import tornado.gen
import tornado.options as opt
import tornado.web

import cloudplayer.api.model


class HTTPHandler(tornado.web.RequestHandler):

    SUPPORTED_METHODS = ('GET', 'POST', 'DELETE', 'PUT', 'OPTIONS')

    def __init__(self, request, application):
        super(HTTPHandler, self).__init__(request, application)
        self.database_session = None

    @property
    def cache(self):
        return redis.Redis(connection_pool=self.application.redis_pool)

    @property
    def db(self):
        if not self.database_session:
            self.database_session = self.application.database.create_session()
        return self.database_session

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
        json.dump(data, super(HTTPHandler, self))
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

    @tornado.gen.coroutine
    def prepare(self):
        user_jwt = self.get_cookie('USER', '')
        try:
            user_dict = jwt.decode(
                user_jwt, self.settings['jwt_secret'], algorithms=['HS256'])
            user = cloudplayer.api.model.User(id=user_dict['id'])
            make_transient_to_detached(user)
            user = self.db.merge(user, load=False)
        except jwt.exceptions.InvalidTokenError:
            user = cloudplayer.api.model.User()
            self.db.add(user)
            self.db.commit()
            user_dict = dict(id=user.id)
            user_jwt = jwt.encode(
                user_dict, self.settings['jwt_secret'], algorithm='HS256')
            self.set_cookie('USER', user_jwt, expires_days=1)
        self.current_user = user

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


class FallbackHandler(HTTPHandler):

    def get(self, *args, **kwargs):
        self.send_error(404, reason='resource not found')
