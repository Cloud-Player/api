"""
    cloudplayer.api.controller.favourite_item
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import tornado.gen

from cloudplayer.api.controller import Controller, ControllerException
from cloudplayer.api.model.favourite import Favourite
from cloudplayer.api.model.favourite_item import FavouriteItem


class FavouriteItemController(Controller):

    __model__ = FavouriteItem

    @tornado.gen.coroutine
    def query(self, ids, kw):
        # TODO: Resolve this workaround with dynamic parent resolution
        favourite = self.db.query(Favourite).get(
            (ids.pop('favourite_id'), ids.pop('favourite_provider_id')))
        kw.pop('favourite_id', None)
        kw.pop('favourite_provider_id', None)
        if not favourite:
            raise ControllerException(404, 'favourite not found')
        kw['favourite'] = favourite
        query = yield super().query(ids, kw)
        return query
