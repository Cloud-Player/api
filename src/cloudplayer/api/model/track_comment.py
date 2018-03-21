"""
    cloudplayer.api.model.track_comment
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.access import Allow, Everyone, Read, Fields
from cloudplayer.api.model import Transient


class TrackComment(Transient):

    __acl__ = (
        Allow(Everyone, Read, Fields(
            'id',
            'provider_id',
            'account.id',
            'account.provider_id',
            'account.title',
            'account.image.small',
            'account.image.medium',
            'account.image.large',
            'body',
            'timestamp',
            'track_id',
            'track_provider_id',
            'created'
        )),
    )

    id = None
    provider_id = None

    account = None

    body = None
    timestamp = None
    track_id = None
    track_provider_id = None
