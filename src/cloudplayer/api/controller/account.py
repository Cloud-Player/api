"""
    cloudplayer.api.controller.account
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.model.account import Account
import cloudplayer.api.controller


class AccountController(cloudplayer.api.controller.Controller):

    __model__ = Account
    __policies__ = []