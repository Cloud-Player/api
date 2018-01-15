"""
    cloudplayer.api.http.favourite
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.controller.favourite import FavouriteController
from cloudplayer.api.http import HTTPHandler
from cloudplayer.api.handler import EntityMixin, CollectionMixin


class Entity(EntityMixin, HTTPHandler):

    __controller__ = FavouriteController

    SUPPORTED_METHODS = ('GET', 'OPTIONS')


class Collection(CollectionMixin, HTTPHandler):

    __controller__ = FavouriteController

    SUPPORTED_METHODS = ('GET', 'OPTIONS')
