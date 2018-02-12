"""
    cloudplayer.api.http.provider
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.controller.provider import ProviderController
from cloudplayer.api.handler import CollectionMixin, EntityMixin
from cloudplayer.api.http import HTTPHandler


class Entity(EntityMixin, HTTPHandler):

    __controller__ = ProviderController

    SUPPORTED_METHODS = ('GET',)


class Collection(CollectionMixin, HTTPHandler):

    __controller__ = ProviderController

    SUPPORTED_METHODS = ('GET',)
