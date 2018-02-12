"""
    cloudplayer.api.http.playlist
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.controller.playlist import PlaylistController
from cloudplayer.api.handler import CollectionMixin, EntityMixin
from cloudplayer.api.http import HTTPHandler


class Entity(EntityMixin, HTTPHandler):

    __controller__ = PlaylistController

    SUPPORTED_METHODS = ('GET', 'PATCH', 'DELETE', 'OPTIONS')


class Collection(CollectionMixin, HTTPHandler):

    __controller__ = PlaylistController

    SUPPORTED_METHODS = ('GET', 'POST', 'OPTIONS')
