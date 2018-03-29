"""
    cloudplayer.api.http.session
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.controller.session import SessionController
from cloudplayer.api.handler import CollectionMixin
from cloudplayer.api.http import HTTPHandler


class Collection(CollectionMixin, HTTPHandler):

    __controller__ = SessionController

    SUPPORTED_METHODS = ('POST', 'OPTIONS')
