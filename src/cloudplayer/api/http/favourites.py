"""
    cloudplayer.api.http.favourites
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.controller.favourites import FavouritesController
from cloudplayer.api.http import HTTPHandler
from cloudplayer.api.handler import EntityMixin, CollectionMixin


class Entity(EntityMixin, HTTPHandler):

    __controller__ = FavouritesController

    SUPPORTED_METHODS = ('GET', 'OPTIONS')


class Collection(CollectionMixin, HTTPHandler):

    __controller__ = FavouritesController

    SUPPORTED_METHODS = ('GET', 'OPTIONS')
