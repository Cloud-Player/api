"""
    cloudplayer.api.controller.user
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.model.user import User

import cloudplayer.api.controller


class UserController(cloudplayer.api.controller.Controller):

    __model__ = User
    __policies__ = []
