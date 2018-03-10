"""
    cloudplayer.api.controller.account
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import tornado.gen

import cloudplayer.api.controller
from cloudplayer.api.access import Available
from cloudplayer.api.model.account import Account


class AccountController(cloudplayer.api.controller.Controller):

    __model__ = Account

    @tornado.gen.coroutine
    def read(self, ids, fields=Available):
        if ids['id'] == 'me':
            ids['id'] = self.current_user.get(ids['provider_id'], 'me')
        entity = yield super().read(ids)
        return entity
