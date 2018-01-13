"""
    cloudplayer.api.controller.favourites_item
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.model.favourites_item import FavouritesItem
import cloudplayer.api.controller


class FavouritesItemController(cloudplayer.api.controller.Controller):

    __model__ = FavouritesItem
    __policies__ = []
