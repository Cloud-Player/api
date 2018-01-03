"""
    cloudplayer.api.user
    ~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
import tornado.gen

from cloudplayer.api.model import User
import cloudplayer.api.handler


class Entity(cloudplayer.api.handler.HTTPHandler):

    __model__ = User

    @tornado.gen.coroutine
    def get(self, id):
        if id == 'me':
            id = self.current_user['user_id']

        user = self.db.query(
            User
        ).filter(
            User.id == id
        ).one_or_none()

        yield self.write(user)

class Collection(cloudplayer.api.handler.HTTPHandler):

    __model__ = User

    @tornado.gen.coroutine
    def get(self, id):
        users = self.db.query(
            User
        ).all()

        yield self.write(users)
