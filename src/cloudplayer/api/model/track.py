"""
    cloudplayer.api.model.track
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.access import Allow, Everyone, Read, Fields
from cloudplayer.api.model import Transient


class Track(Transient):

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
            'aspect_ratio',
            'duration',
            'favourite_count',
            'image.small',
            'image.medium',
            'image.large',
            'play_count',
            'title',
            'created'
        )),
    )

    id = None
    provider_id = None

    account = None

    aspect_ratio = None
    duration = None
    favourite_count = None
    image = None
    play_count = None
    title = None
