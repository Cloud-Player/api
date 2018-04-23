"""
    cloudplayer.api.model.track
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import datetime

import isodate

from cloudplayer.api.access import Allow, Everyone, Fields, Read
from cloudplayer.api.model import Transient
from cloudplayer.api.model.account import Account
from cloudplayer.api.model.image import Image


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

    @classmethod
    def from_provider(cls, provider_id, track):
        if provider_id == 'soundcloud':
            return cls.from_soundcloud(track)
        elif provider_id == 'youtube':
            return cls.from_youtube(track)
        else:
            raise ValueError('unsupported provider')

    @classmethod
    def from_soundcloud(cls, track):
        user = track['user']
        artist = Account(
            id=user['id'],
            provider_id='soundcloud',
            title=user['username'],
            image=Image.from_soundcloud(user.get('avatar_url')))

        return cls(
            id=track['id'],
            provider_id='soundcloud',
            account=artist,
            aspect_ratio=1.0,
            duration=int(track['duration'] / 1000.0),
            favourite_count=track.get('favoritings_count', 0),
            image=Image.from_soundcloud(track.get('artwork_url')),
            play_count=track.get('playback_count', 0),
            title=track['title'],
            created=datetime.datetime.strptime(
                track['created_at'], '%Y/%m/%d %H:%M:%S %z'))

    @classmethod
    def from_youtube(cls, track):
        snippet = track['snippet']
        player = track['player']
        statistics = track['statistics']
        duration = isodate.parse_duration(track['contentDetails']['duration'])

        artist = Account(
            id=snippet['channelId'],
            provider_id='youtube',
            image=None,
            title=snippet['channelTitle'])

        return cls(
            id=track['id'],
            provider_id='youtube',
            account=artist,
            aspect_ratio=(
                float(player['embedHeight']) / float(player['embedWidth'])),
            duration=int(duration.total_seconds()),
            favourite_count=statistics.get('likeCount', 0),
            image=Image.from_youtube(snippet.get('thumbnails')),
            play_count=statistics.get('viewCount', 0),
            title=snippet['title'],
            created=datetime.datetime.strptime(
                snippet['publishedAt'], '%Y-%m-%dT%H:%M:%S.%fZ'))
