"""
    cloudplayer.api.http.favourite_item
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.controller.favourite_item import (
    CloudplayerFavouriteItemController,
    SoundcloudFavouriteItemController,
    YoutubeFavouriteItemController)
from cloudplayer.api.handler import CollectionMixin, EntityMixin
from cloudplayer.api.http import HTTPHandler


class CloudplayerEntity(EntityMixin, HTTPHandler):

    __controller__ = CloudplayerFavouriteItemController

    SUPPORTED_METHODS = ('DELETE', 'OPTIONS')


class CloudplayerCollection(CollectionMixin, HTTPHandler):

    __controller__ = CloudplayerFavouriteItemController

    SUPPORTED_METHODS = ('GET', 'POST', 'OPTIONS')


class SoundcloudCollection(CollectionMixin, HTTPHandler):

    __controller__ = SoundcloudFavouriteItemController

    SUPPORTED_METHODS = ('GET', 'OPTIONS')


class YoutubeCollection(CollectionMixin, HTTPHandler):

    __controller__ = YoutubeFavouriteItemController

    SUPPORTED_METHODS = ('GET', 'OPTIONS')
