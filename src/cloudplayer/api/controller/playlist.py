"""
    cloudplayer.api.controller.playlist
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.model.playlist import Playlist

import cloudplayer.api.controller


class PlaylistController(cloudplayer.api.controller.Controller):

    __model__ = Playlist
    __policies__ = []
