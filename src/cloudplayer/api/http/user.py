"""
    cloudplayer.api.http.user
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.controller.user import UserController
from cloudplayer.api.handler import EntityMixin
from cloudplayer.api.http import HTTPHandler


class Entity(EntityMixin, HTTPHandler):

    __controller__ = UserController

    SUPPORTED_METHODS = ('GET',)
