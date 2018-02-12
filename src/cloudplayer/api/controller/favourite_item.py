"""
    cloudplayer.api.controller.favourite_item
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.model.favourite_item import FavouriteItem
import cloudplayer.api.controller


class FavouriteItemController(cloudplayer.api.controller.Controller):

    __model__ = FavouriteItem
