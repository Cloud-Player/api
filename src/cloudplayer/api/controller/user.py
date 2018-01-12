"""
    cloudplayer.api.controller.user
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.model.user import User
import cloudplayer.api.controller


class UserController(cloudplayer.api.controller.Controller):

    __model__ = User
    __policies__ = []

    def read(self, ids):
        if ids['id'] == 'me':
            ids['id'] = self.current_user['user_id']
        entity = super().read(ids)
        if not entity and ids['id'] == self.current_user['user_id']:
            self.current_user.clear()
        return entity
