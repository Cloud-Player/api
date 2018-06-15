"""
    cloudplayer.api.controller.favourite_item
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import tornado.gen

from cloudplayer.api.access import Available
from cloudplayer.api.controller import Controller, ControllerException
from cloudplayer.api.controller.track import TrackController
from cloudplayer.api.model.favourite import Favourite
from cloudplayer.api.model.favourite_item import FavouriteItem


class FavouriteItemController(Controller):

    __model__ = FavouriteItem


class CloudplayerFavouriteItemController(Controller):

    __provider__ = 'cloudplayer'
    __model__ = FavouriteItem


class SoundcloudFavouriteItemController(Controller):

    __provider__ = 'soundcloud'
    __model__ = FavouriteItem


class YoutubeFavouriteItemController(Controller):

    __provider__ = 'youtube'
    __model__ = FavouriteItem

    @tornado.gen.coroutine
    def search(self, ids, kw, fields=Available):
        track_controller = TrackController.for_provider(
            self.__provider__, self.db, self.current_user)

        track_ids = {'provider_id': self.__provider__, 'ids': []}
        track_kw = {'rating': 'like'}
        tracks = yield track_controller.mread(
            track_ids, track_kw, fields=fields)
        return tracks
