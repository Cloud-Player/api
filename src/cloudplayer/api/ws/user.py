"""
    cloudplayer.api.ws.user
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
import tornado.gen

from cloudplayer.api.controller.user import UserController
from cloudplayer.api.ws import WSHandler
from cloudplayer.api.handler import EntityMixin


class Entity(EntityMixin, WSHandler):

    __controller__ = UserController

    SUPPORTED_METHODS = ('GET',)
