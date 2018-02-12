"""
    cloudplayer.api.controller.account
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.model.account import Account
from cloudplayer.api.policy import Secure
import cloudplayer.api.controller


class AccountController(cloudplayer.api.controller.Controller):

    __model__ = Account
    __policies__ = [Secure]
