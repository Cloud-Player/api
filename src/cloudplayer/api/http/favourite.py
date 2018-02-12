"""
    cloudplayer.api.http.favourite
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.controller.favourite import FavouriteController
from cloudplayer.api.handler import CollectionMixin, EntityMixin
from cloudplayer.api.http import HTTPHandler


class Entity(EntityMixin, HTTPHandler):

    __controller__ = FavouriteController

    SUPPORTED_METHODS = ('GET', 'OPTIONS')


class Collection(CollectionMixin, HTTPHandler):

    __controller__ = FavouriteController

    SUPPORTED_METHODS = ('GET', 'OPTIONS')
