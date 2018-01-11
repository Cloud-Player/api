"""
    cloudplayer.api.controller.token
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.model.token import Token
from cloudplayer.api.policy import Secure
import cloudplayer.api.controller


class TokenController(cloudplayer.api.controller.Controller):

    __model__ = Token
    __policies__ = [Secure]

    def create(self, ids, **kw):
        return super().create({})
