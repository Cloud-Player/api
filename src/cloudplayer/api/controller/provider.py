"""
    cloudplayer.api.controller.provider
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.model.provider import Provider

import cloudplayer.api.controller


class ProviderController(cloudplayer.api.controller.Controller):

    __model__ = Provider
    __policies__ = []
