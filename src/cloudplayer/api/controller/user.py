"""
    cloudplayer.api.controller.user
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.controller import Controller, ControllerException
from cloudplayer.api.model.user import User


class UserController(Controller):

    __model__ = User

    async def read(self, ids):
        if ids['id'] == 'me':
            ids['id'] = self.current_user['user_id']
        try:
            entity = await super().read(ids)
        except ControllerException:
            if ids['id'] == self.current_user['user_id']:
                self.current_user.clear()
            raise
        return entity
