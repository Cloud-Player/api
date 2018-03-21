"""
    cloudplayer.api.http.track_comment
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.controller.track_comment import \
    SoundcloudTrackCommentController
from cloudplayer.api.handler import CollectionMixin
from cloudplayer.api.http import HTTPHandler


class Soundcloud(CollectionMixin, HTTPHandler):

    __controller__ = SoundcloudTrackCommentController

    SUPPORTED_METHODS = ('GET', 'OPTIONS')
