"""
    cloudplayer.api.controller.favourite_item
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.model.favourite_item import FavouriteItem
from cloudplayer.api.policy import Owned
import cloudplayer.api.controller


class FavouriteItemController(cloudplayer.api.controller.Controller):

    __model__ = FavouriteItem
    __policies__ = [Owned]
