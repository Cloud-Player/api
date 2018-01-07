"""
    cloudplayer.api.handler.account
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.controller.account import AccountController
import cloudplayer.api.handler


class Entity(cloudplayer.api.handler.EntityHandler):

    __controller__ = AccountController

    SUPPORTED_METHODS = ['GET']
