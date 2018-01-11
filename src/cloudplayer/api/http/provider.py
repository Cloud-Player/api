"""
    cloudplayer.api.http.provider
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.controller.provider import ProviderController
from cloudplayer.api.http import HTTPHandler
from cloudplayer.api.handler import EntityMixin, CollectionMixin


class Entity(EntityMixin, HTTPHandler):

    __controller__ = ProviderController

    SUPPORTED_METHODS = ('GET',)


class Collection(CollectionMixin, HTTPHandler):

    __controller__ = ProviderController

    SUPPORTED_METHODS = ('GET',)
