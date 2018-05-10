"""
    cloudplayer.api.controller.track
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import datetime
import traceback
import urllib.parse

import tornado.escape
import tornado.gen

from cloudplayer.api.access import Available
from cloudplayer.api.controller import Controller
from cloudplayer.api.model.track import Track
from cloudplayer.api.util import chunk_range, squeeze


class TrackController(Controller):

    SEARCH_MAX_SIZE = 50


class SoundcloudTrackController(TrackController):

    __provider__ = 'soundcloud'

    SEARCH_YOUTUBE_DURATION = {
        'any': {},
        'long': {
            'duration[from]':
                int(datetime.timedelta(minutes=20).total_seconds() * 1000) + 1
            },
        'medium': {
            'duration[from]':
                int(datetime.timedelta(minutes=4).total_seconds() * 1000) + 1,
            'duration[to]':
                int(datetime.timedelta(minutes=20).total_seconds() * 1000)
            },
        'short': {
            'duration[to]':
                int(datetime.timedelta(minutes=4).total_seconds() * 1000)
        }
    }

    @tornado.gen.coroutine
    def read(self, ids, fields=Available):
        response = yield self.fetch(
            ids['provider_id'], '/tracks/{}'.format(ids['id']))
        track = tornado.escape.json_decode(response.body)
        entity = Track.from_soundcloud(track)
        account = self.get_account(entity.provider_id)
        self.policy.grant_read(account, entity, fields)
        return entity

    @tornado.gen.coroutine
    def search(self, ids, kw, fields=Available):
        params = {
            'q': kw.get('q'),
            'filter': 'public',
            'limit': self.SEARCH_MAX_SIZE}
        if 'duration' in kw:
            duration = self.SEARCH_YOUTUBE_DURATION.get(kw['duration'], {})
            params.update(duration.copy())
        response = yield self.fetch(
            ids['provider_id'], '/tracks', params=params)
        track_list = tornado.escape.json_decode(response.body)
        entities = []
        account = self.get_account(ids['provider_id'])
        for track in track_list:
            try:
                entity = Track.from_soundcloud(track)
            except (KeyError, ValueError):
                traceback.print_exc()
                continue
            self.policy.grant_read(account, entity, fields)
            entities.append(entity)
        return entities


class YoutubeTrackController(TrackController):

    __provider__ = 'youtube'

    MREAD_YOUTUBE_FIELDS = squeeze("""
        items(
        id,
        snippet(
            channelId,
            channelTitle,
            thumbnails(
                default/url,
                medium/url,
                high/url),
            title,
            publishedAt),
        contentDetails/duration,
        statistics(
            viewCount,
            likeCount),
        player(
            embedWidth,
            embedHeight))
    """)

    SEARCH_YOUTUBE_FIELDS = squeeze("""
        items/id/videoId
    """)

    @tornado.gen.coroutine
    def read(self, ids, fields=Available):
        ids['ids'] = [ids.pop('id')]
        entities = yield self.mread(ids, fields=fields)
        if entities:
            return entities[0]

    @tornado.gen.coroutine
    def mread(self, ids, fields=Available):
        params = {
            'id': ','.join(urllib.parse.quote(i, safe='') for i in ids['ids']),
            'part': 'snippet,contentDetails,player,statistics',
            'fields': self.MREAD_YOUTUBE_FIELDS,
            'maxWidth': '320'}
        response = yield self.fetch(
            ids['provider_id'], '/videos', params=params)
        track_list = tornado.escape.json_decode(response.body)
        entities = []
        account = self.get_account(ids['provider_id'])
        for track in track_list['items']:
            try:
                entity = Track.from_youtube(track)
            except (KeyError, ValueError):
                traceback.print_exc()
                continue
            self.policy.grant_read(account, entity, fields)
            entities.append(entity)
        return entities

    @tornado.gen.coroutine
    def search(self, ids, kw, fields=Available):
        params = {
            'q': kw.get('q'),
            'part': 'snippet',
            'type': 'video',
            'videoEmbeddable': 'true',
            'videoSyndicated': 'true',
            'maxResults': self.SEARCH_MAX_SIZE,
            'fields': self.SEARCH_YOUTUBE_FIELDS}
        if 'rating' in kw:
            params['myRating'] = kw['rating']
        if kw.get('duration') in ('any', 'long', 'medium', 'short'):
            params['videoDuration'] = kw['duration']
        response = yield self.fetch(
            ids['provider_id'], '/search', params=params)
        search_result = tornado.escape.json_decode(response.body)
        video_ids = [i['id']['videoId'] for i in search_result['items']]

        futures = []
        for i, j in chunk_range(params['maxResults']):
            futures.append(self.mread(
                {'provider_id': ids['provider_id'], 'ids': video_ids[i: j]},
                fields=fields))

        entities = yield futures
        return entities
