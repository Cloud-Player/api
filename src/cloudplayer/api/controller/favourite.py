"""
    cloudplayer.api.controller.favourite
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.access import Available
from cloudplayer.api.controller import Controller
from cloudplayer.api.model.favourite import Favourite


class FavouriteController(Controller):

    __model__ = Favourite

    async def read(self, ids, fields=Available):
        if ids['id'] == 'mine':
            account = self.get_account(ids['provider_id'])
            if account:
                ids['id'] = account.favourite.id
        return await super().read(ids, fields=fields)
