"""
    cloudplayer.api.controller.favourite_item
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import tornado.gen

from cloudplayer.api.controller import Controller
from cloudplayer.api.model.favourite_item import FavouriteItem


class FavouriteItemController(Controller):

    __model__ = FavouriteItem

    @tornado.gen.coroutine
    def create(self, ids, kw, **params):
        if 'account_provider_id' not in kw:
            kw['account_provider_id'] = kw['favourite_provider_id']
        if 'account_id' not in kw:
            kw['account_id'] = self.accounts[kw['account_provider_id']]
        entity = yield super().create(ids, kw, **params)
        return entity
