"""
    cloudplayer.api.ws.playlist
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.controller.playlist import PlaylistController
from cloudplayer.api.handler import EntityMixin
from cloudplayer.api.ws import WSHandler


class Entity(EntityMixin, WSHandler):

    __controller__ = PlaylistController

    SUPPORTED_METHODS = ('GET', 'PUT', 'SUB', 'UNSUB')
