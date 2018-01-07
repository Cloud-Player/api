"""
    cloudplayer.api.controller.track
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.model.track import Track

import cloudplayer.api.controller


class TrackController(cloudplayer.api.controller.Controller):

    __model__ = Track
    __policies__ = []
