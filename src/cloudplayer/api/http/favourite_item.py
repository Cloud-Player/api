"""
    cloudplayer.api.http.favourite_item
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.controller.favourite_item import FavouriteItemController
from cloudplayer.api.handler import CollectionMixin, EntityMixin
from cloudplayer.api.http import HTTPHandler


class Entity(EntityMixin, HTTPHandler):

    __controller__ = FavouriteItemController

    SUPPORTED_METHODS = ('GET', 'DELETE', 'OPTIONS')


class Collection(CollectionMixin, HTTPHandler):

    __controller__ = FavouriteItemController

    SUPPORTED_METHODS = ('GET', 'POST', 'OPTIONS')
