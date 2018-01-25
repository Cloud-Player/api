"""
    cloudplayer.api.controller.track
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
import datetime

import isodate
import tornado.gen

from cloudplayer.api.controller import Controller
from cloudplayer.api.model.account import Account
from cloudplayer.api.model.image import Image
from cloudplayer.api.policy import Open


class SoundcloudTrackController(Controller):

    __policies__ = [Open]

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
        return {
            'id': ids['id'],
            'provider_id': ids['provider_id'],
            'title': track['title'],
            'account': Account(
                id=account['id'],
                provider_id=ids['provider_id'],
                title=account['username'],
                image=Image(
                    small=account['avatar_url'],
                    medium=account['avatar_url'].replace('large', 't300x300'),
                    large=account['avatar_url'].replace('large', 't500x500')
                )
            ),
            'account_id': track['user_id'],
            'account_provider_id': ids['provider_id'],
            'play_count': track['playback_count'],
            'favourite_count': track['favoritings_count'],
            'aspect_ratio': 1.0,
            'created': datetime.datetime.strptime(
                track['created_at'], self.DATE_FORMAT),
            'duration': int(track['duration'] / 1000.0),
            'image': image
        }


class YoutubeTrackController(Controller):

    __policies__ = [Open]

    DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

    @tornado.gen.coroutine
    def read(self, ids):
        params = {
            'id': ids['id'], 'part': 'snippet,player,contentDetails,statistics',
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
        return {
            'id': ids['id'],
            'provider_id': ids['provider_id'],
            'title': snippet['title'],
            'account': Account(
                id=snippet['channelId'],
                provider_id=ids['provider_id'],
                title=snippet['channelTitle'],
            ),
            'account_id': snippet['channelId'],
            'account_provider_id': ids['provider_id'],
            'play_count': statistics['viewCount'],
            'favourite_count': statistics['favoriteCount'],
            'aspect_ratio': (
                float(player['embedHeight']) / float(player['embedWidth'])),
            'created': datetime.datetime.strptime(
                snippet['publishedAt'], self.DATE_FORMAT),
            'duration': int(duration.total_seconds()),
            'image': image
        }



