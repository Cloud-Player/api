"""
    cloudplayer.api.handler.playlist
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.controller.playlist import PlaylistController
import cloudplayer.api.handler


class Entity(cloudplayer.api.handler.EntityHandler):

    __controller__ = PlaylistController

    SUPPORTED_METHODS = ['GET', 'PATCH', 'DELETE']


class Collection(cloudplayer.api.handler.CollectionHandler):

    __controller__ = PlaylistController

    SUPPORTED_METHODS = ['GET', 'POST']
