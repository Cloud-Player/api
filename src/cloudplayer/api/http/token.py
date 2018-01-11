"""
    cloudplayer.api.http.token
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.controller.token import TokenController
from cloudplayer.api.http import HTTPHandler
from cloudplayer.api.handler import EntityMixin, CollectionMixin


class Entity(EntityMixin, HTTPHandler):

    __controller__ = TokenController

    SUPPORTED_METHODS = ('GET', 'PUT', 'OPTIONS')


class Collection(EntityMixin, HTTPHandler):

    __controller__ = TokenController

    SUPPORTED_METHODS = ('POST', 'OPTIONS')
