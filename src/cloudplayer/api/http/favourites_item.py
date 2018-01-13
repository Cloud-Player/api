"""
    cloudplayer.api.http.favourites_item
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.controller.favourites_item import FavouritesItemController
from cloudplayer.api.http import HTTPHandler
from cloudplayer.api.handler import EntityMixin, CollectionMixin


class Entity(EntityMixin, HTTPHandler):

    __controller__ = FavouritesItemController

    SUPPORTED_METHODS = ('GET', 'DELETE', 'OPTIONS')


class Collection(CollectionMixin, HTTPHandler):

    __controller__ = FavouritesItemController

    SUPPORTED_METHODS = ('GET', 'POST', 'OPTIONS')
