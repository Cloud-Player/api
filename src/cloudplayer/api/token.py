"""
    cloudplayer.api.token
    ~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
import json
import string
import secrets

import tornado.gen
import tornado.web

import cloudplayer.api.handler


class Entity(cloudplayer.api.handler.HTTPHandler):

    @tornado.gen.coroutine
    def get(self, id):
        token = self.cache.get(id)
        if not token:
            raise tornado.web.HTTPError(404, 'token does not exist')
        token = json.loads(token)
        user = token.pop('user', None)
        if user:
            self.current_user = user
            self.cache.delete(id)
        self.write(token)

    @tornado.gen.coroutine
    def put(self, id):
        if not self.cache.get(id):
            raise tornado.web.HTTPError(404, 'token does not exist')
        token = {'id': id, 'claimed': True, 'user': self.current_user}
        self.cache.set(id, json.dumps(token))
        token.pop('user')
        self.write(token)


class Collection(cloudplayer.api.handler.HTTPHandler):

    ALPHABET = string.ascii_lowercase + string.digits
    TOKEN_EXPIRATION = 60 * 5

    @tornado.gen.coroutine
    def post(self):
        id = ''.join(secrets.choice(self.ALPHABET) for i in range(6))
        token = {'id': id, 'claimed': False}
        self.cache.set(id, json.dumps(token))
        self.cache.expire(id, self.TOKEN_EXPIRATION)
        self.write(token)
