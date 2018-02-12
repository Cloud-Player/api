"""
    cloudplayer.api.http.track
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.controller.track import SoundcloudTrackController
from cloudplayer.api.controller.track import YoutubeTrackController
from cloudplayer.api.handler import EntityMixin
from cloudplayer.api.http import HTTPHandler


class Soundcloud(EntityMixin, HTTPHandler):

    __controller__ = SoundcloudTrackController

    SUPPORTED_METHODS = ('GET', 'OPTIONS')


class Youtube(EntityMixin, HTTPHandler):

    __controller__ = YoutubeTrackController

    SUPPORTED_METHODS = ('GET', 'OPTIONS')
