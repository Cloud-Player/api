"""
    cloudplayer.api.controller.track
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import datetime

import isodate
import tornado.escape
import tornado.gen

from cloudplayer.api.controller import Controller
from cloudplayer.api.model.account import Account
from cloudplayer.api.model.image import Image


def create_track_controller(provider_id, db, current_user=None):
    if provider_id == 'soundcloud':
        return SoundcloudTrackController(db, current_user)
    elif provider_id == 'youtube':
        return YoutubeTrackController(db, current_user)
    else:
        raise ValueError('unsupported provider')


class SoundcloudTrackController(Controller):

    DATE_FORMAT = '%Y/%m/%d %H:%M:%S %z'

    @tornado.gen.coroutine
    def read(self, ids):
        response = yield self.fetch(
            ids['provider_id'], '/tracks/{}'.format(ids['id']))
        track = tornado.escape.json_decode(response.body)
        account = track['user']
        if track.get('artwork_url'):
            image = Image(
                small=track['artwork_url'] or None,
                medium=track['artwork_url'].replace('large', 't300x300'),
                large=track['artwork_url'].replace('large', 't500x500')
            )
        else:
            image = None
        account = Account(
            id=account['id'],
            provider_id=ids['provider_id'],
            image=Image(
                small=account['avatar_url'],
                medium=account['avatar_url'].replace('large', 't300x300'),
                large=account['avatar_url'].replace('large', 't500x500')
            ),
            title=account['username']
        )
        return {
            'id': ids['id'],
            'provider_id': ids['provider_id'],
            'account': account,
            'aspect_ratio': 1.0,
            'duration': int(track['duration'] / 1000.0),
            'favourite_count': track.get('favoritings_count', 0),
            'image': image,
            'play_count': track.get('playback_count', 0),
            'title': track['title'],
            'created': datetime.datetime.strptime(
                track['created_at'], self.DATE_FORMAT),
            'updated': None
        }


class YoutubeTrackController(Controller):

    DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

    @tornado.gen.coroutine
    def read(self, ids):
        params = {
            'id': ids['id'],
            'part': 'snippet,player,contentDetails,statistics',
            'maxWidth': '320'}
        response = yield self.fetch(
            ids['provider_id'], '/videos', params=params)
        track_list = tornado.escape.json_decode(response.body)
        if not track_list['items']:
            return
        track = track_list['items'][0]
        snippet = track['snippet']
        player = track['player']
        statistics = track['statistics']
        duration = isodate.parse_duration(track['contentDetails']['duration'])
        image = Image(
            small=snippet['thumbnails']['default']['url'],
            medium=snippet['thumbnails']['medium']['url'],
            large=snippet['thumbnails']['high']['url']
        )
        account = Account(
            id=snippet['channelId'],
            provider_id=ids['provider_id'],
            image=None,
            title=snippet['channelTitle']
        )
        return {
            'id': ids['id'],
            'provider_id': ids['provider_id'],
            'account': account,
            'aspect_ratio': (
                float(player['embedHeight']) / float(player['embedWidth'])),
            'duration': int(duration.total_seconds()),
            'favourite_count': statistics['favoriteCount'],
            'image': image,
            'play_count': statistics['viewCount'],
            'title': snippet['title'],
            'created': datetime.datetime.strptime(
                snippet['publishedAt'], self.DATE_FORMAT),
            'updated': None
        }
