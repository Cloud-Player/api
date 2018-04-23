"""
    cloudplayer.api.controller.track
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import functools
import urllib.parse

import tornado.escape
import tornado.gen

from cloudplayer.api.access import Available
from cloudplayer.api.controller import Controller
from cloudplayer.api.model.track import Track
from cloudplayer.api.util import chunk_range


class TrackController(Controller):

    @staticmethod
    def for_provider(provider_id, db, current_user=None):
        if provider_id == 'soundcloud':
            return SoundcloudTrackController(db, current_user)
        elif provider_id == 'youtube':
            return YoutubeTrackController(db, current_user)
        else:
            raise ValueError('unsupported provider')


class SoundcloudTrackController(TrackController):

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
    def search(self, ids, fields=Available):
        pass


class YoutubeTrackController(TrackController):

    MREAD_YOUTUBE_FIELDS = ''.join("""
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
    """.split())

    SEARCH_YOUTUBE_FIELDS = ''.join("""
        items/id/videoId
    """.split())

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
        for track in track_list['items']:
            entity = Track.from_youtube(track)
            account = self.get_account(entity.provider_id)
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
            'maxResults': 50,
            'fields': self.SEARCH_YOUTUBE_FIELDS}
        response = yield self.fetch(
            ids['provider_id'], '/search', params=params)
        search_result = tornado.escape.json_decode(response.body)
        video_ids = [i['id']['videoId'] for i in search_result['items']]

        futures = []
        for i, j in chunk_range(params['maxResults'], 4):
            futures.append(self.mread(
                {'provider_id': ids['provider_id'], 'ids': video_ids[i: j]},
                fields=fields))

        entities = yield futures
        return entities
