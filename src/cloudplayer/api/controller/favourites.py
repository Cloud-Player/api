"""
    cloudplayer.api.controller.favourites
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.model.favourites import Favourites
import cloudplayer.api.controller


class FavouritesController(cloudplayer.api.controller.Controller):

    __model__ = Favourites
    __policies__ = []
