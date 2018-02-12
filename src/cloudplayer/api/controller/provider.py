"""
    cloudplayer.api.controller.provider
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.model.provider import Provider
from cloudplayer.api.policy import Open
import cloudplayer.api.controller


class ProviderController(cloudplayer.api.controller.Controller):

    __model__ = Provider
    __policies__ = [Open]
