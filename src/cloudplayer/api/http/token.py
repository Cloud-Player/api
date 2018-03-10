"""
    cloudplayer.api.http.token
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.controller.token import TokenController
from cloudplayer.api.handler import CollectionMixin, EntityMixin
from cloudplayer.api.http import HTTPHandler


class Entity(EntityMixin, HTTPHandler):

    __controller__ = TokenController

    SUPPORTED_METHODS = ('GET', 'PUT', 'OPTIONS')


class Collection(CollectionMixin, HTTPHandler):

    __controller__ = TokenController

    SUPPORTED_METHODS = ('POST', 'OPTIONS')
