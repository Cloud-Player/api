"""
    cloudplayer.api.controller.playlist_item
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.model.playlist_item import PlaylistItem
import cloudplayer.api.controller


class PlaylistItemController(cloudplayer.api.controller.Controller):

    __model__ = PlaylistItem
