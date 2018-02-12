"""
    cloudplayer.api.http.account
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.controller.account import AccountController
from cloudplayer.api.http import HTTPHandler
from cloudplayer.api.handler import EntityMixin


class Entity(EntityMixin, HTTPHandler):

    __controller__ = AccountController

    SUPPORTED_METHODS = ('GET', 'OPTIONS')
