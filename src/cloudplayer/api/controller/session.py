"""
    cloudplayer.api.controller.session
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.controller import Controller
from cloudplayer.api.model.session import Session


class SessionController(Controller):

    __model__ = Session
