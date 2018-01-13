"""
    cloudplayer.api.controller.favourites
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.model.account import Account
from cloudplayer.api.model.favourites import Favourites
import cloudplayer.api.controller


class FavouritesController(cloudplayer.api.controller.Controller):

    __model__ = Favourites
    __policies__ = []

    def read(self, ids):
        if ids['id'] == 'mine':
            provider_id = ids['provider_id']
            account_id = self.current_user[provider_id]
            account = self.db.query(Account).get((account_id, provider_id))
            ids['id'] = account.favourites.id
        return super().read(ids)
