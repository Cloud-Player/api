"""
    cloudplayer.api.controller.user
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import tornado.gen

from cloudplayer.api.controller import Controller, ControllerException
from cloudplayer.api.model.user import User


class UserController(Controller):

    __model__ = User

    @tornado.gen.coroutine
    def read(self, ids):
        if ids['id'] == 'me':
            ids['id'] = self.current_user['user_id']
        try:
            entity = yield super().read(ids)
        except ControllerException:
            if ids['id'] == self.current_user['user_id']:
                self.current_user.clear()
            raise
        return entity
