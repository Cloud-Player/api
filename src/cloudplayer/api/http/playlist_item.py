"""
    cloudplayer.api.http.playlist_item
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.controller.playlist_item import PlaylistItemController
from cloudplayer.api.http import HTTPHandler
from cloudplayer.api.handler import EntityMixin, CollectionMixin


class Entity(EntityMixin, HTTPHandler):

    __controller__ = PlaylistItemController

    SUPPORTED_METHODS = ('GET', 'PATCH', 'DELETE', 'OPTIONS')


class Collection(CollectionMixin, HTTPHandler):

    __controller__ = PlaylistItemController

    SUPPORTED_METHODS = ('GET', 'POST', 'OPTIONS')
