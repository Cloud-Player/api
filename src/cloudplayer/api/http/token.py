"""
    cloudplayer.api.http.token
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.controller.token import TokenController
from cloudplayer.api.handler import EntityMixin, CollectionMixin
from cloudplayer.api.http import HTTPHandler


class Entity(EntityMixin, HTTPHandler):

    __controller__ = TokenController

    SUPPORTED_METHODS = ('GET', 'PATCH', 'OPTIONS')


class Collection(CollectionMixin, HTTPHandler):

    __controller__ = TokenController

    SUPPORTED_METHODS = ('POST', 'OPTIONS')
