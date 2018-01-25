"""
    cloudplayer.api.controller.user
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
import tornado.gen

from cloudplayer.api.model.user import User
from cloudplayer.api.policy import Open
import cloudplayer.api.controller


class UserController(cloudplayer.api.controller.Controller):

    __model__ = User
    __policies__ = [Open]

    @tornado.gen.coroutine
    def read(self, ids):
        if ids['id'] == 'me':
            ids['id'] = self.current_user['user_id']
        entity = yield super().read(ids)
        if not entity and ids['id'] == self.current_user['user_id']:
            self.current_user.clear()
        return entity
