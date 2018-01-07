"""
    cloudplayer.api.handler.user
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
import tornado.gen

from cloudplayer.api.controller.user import UserController
import cloudplayer.api.handler


class Entity(cloudplayer.api.handler.EntityHandler):

    __controller__ = UserController

    SUPPORTED_METHODS = ['GET']

    @tornado.gen.coroutine
    def get(self, id=None):
        if id == 'me':
            id = self.current_user['user_id']
        yield super().get(id=id)
