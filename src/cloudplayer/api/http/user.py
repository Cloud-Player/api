"""
    cloudplayer.api.http.user
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.controller.user import UserController
from cloudplayer.api.http import HTTPHandler
from cloudplayer.api.handler import EntityMixin


class Entity(EntityMixin, HTTPHandler):

    __controller__ = UserController

    SUPPORTED_METHODS = ('GET',)
