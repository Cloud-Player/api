"""
    cloudplayer.api.handler.playlist_item
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.controller.playlist_item import PlaylistItemController
import cloudplayer.api.handler


class Entity(cloudplayer.api.handler.EntityHandler):

    __controller__ = PlaylistItemController

    SUPPORTED_METHODS = ['GET', 'PATCH', 'DELETE']


class Collection(cloudplayer.api.handler.CollectionHandler):

    __controller__ = PlaylistItemController

    SUPPORTED_METHODS = ['GET', 'POST']
