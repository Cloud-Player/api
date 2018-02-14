"""
    cloudplayer.api.controller.favourite
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.controller import Controller
from cloudplayer.api.model.favourite import Favourite


class FavouriteController(Controller):

    __model__ = Favourite

    def read(self, ids):
        if ids['id'] == 'mine':
            account = self.accounts[ids['provider_id']]
            ids['id'] = account.favourite.id
        return super().read(ids)
