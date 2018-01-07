"""
    cloudplayer.api.handler.provider
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.controller.provider import ProviderController
import cloudplayer.api.handler


class Entity(cloudplayer.api.handler.EntityHandler):

    __controller__ = ProviderController

    SUPPORTED_METHODS = ['GET']


class Collection(cloudplayer.api.handler.CollectionHandler):

    __controller__ = ProviderController

    SUPPORTED_METHODS = ['GET']
