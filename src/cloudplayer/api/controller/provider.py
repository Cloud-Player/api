"""
    cloudplayer.api.controller.provider
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.controller import Controller
from cloudplayer.api.model.provider import Provider


class ProviderController(Controller):

    __model__ = Provider
