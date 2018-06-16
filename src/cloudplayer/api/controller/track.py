"""
    cloudplayer.api.controller.track
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import datetime
import itertools
import random
import traceback
import urllib.parse

import tornado.escape
import tornado.gen
import tornado.options as opt

from cloudplayer.api.access import Available
from cloudplayer.api.controller import Controller, ControllerException
from cloudplayer.api.model.track import Track
from cloudplayer.api.util import chunk_range, squeeze


class TrackController(Controller):

    MAX_RESULTS = 50

    async def search(self, ids, kw, fields=Available):
        futures = []
        for provider_id in opt.options.providers:
            try:
                controller = self.for_provider(
                    provider_id, self.db, self.current_user)
            except ValueError:
                continue
            local_ids = kw.copy()
            local_ids['provider_id'] = provider_id
            future = controller.search(local_ids, kw, fields=fields)
            futures.append(future)
        entities = await tornado.gen.multi(futures)
        tracks = list(itertools.chain(*entities))
        random.Random(kw.get('q', '')).shuffle(tracks)
        return tracks


class SoundcloudTrackController(TrackController):

    __provider__ = 'soundcloud'

    SEARCH_DURATION = {
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

    async def read(self, ids, fields=Available):
        response = await self.fetch(
            ids['provider_id'], '/tracks/{}'.format(ids['id']))
        track = tornado.escape.json_decode(response.body)
        entity = Track.from_soundcloud(track)
        account = self.get_account(entity.provider_id)
        self.policy.grant_read(account, entity, fields)
        return entity

    async def search(self, ids, kw, fields=Available):
        params = {
            'q': kw.get('q'),
            'filter': 'public',
            'limit': self.MAX_RESULTS}
        if 'duration' in kw:
            duration = self.SEARCH_DURATION.get(kw['duration'], {})
            params.update(duration.copy())
        response = await self.fetch(
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

    MREAD_FIELDS = squeeze("""
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

    SEARCH_FIELDS = squeeze("""
        items/id/videoId
    """)

    async def read(self, ids, fields=Available):
        kw = {'ids': [ids.pop('id')]}
        entities = await self.mread(ids, kw, fields=fields)
        if entities:
            return entities[0]

    async def mread(self, ids, kw, fields=Available):
        params = {
            'part': 'snippet,contentDetails,player,statistics',
            'fields': self.MREAD_FIELDS,
            'maxWidth': '320'}
        if 'ids' in kw:
            params['id'] = ','.join(
                urllib.parse.quote(i, safe='') for i in kw['ids'])
        elif 'rating' in kw:
            params['myRating'] = kw['rating']
            params['maxResults'] = self.MAX_RESULTS
        else:
            raise ControllerException(400, 'missing ids or rating')
        response = await self.fetch(
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

    async def search(self, ids, kw, fields=Available):
        params = {
            'q': kw.get('q'),
            'part': 'snippet',
            'type': 'video',
            'videoEmbeddable': 'true',
            'videoSyndicated': 'true',
            'maxResults': self.MAX_RESULTS,
            'fields': self.SEARCH_FIELDS}
        if kw.get('duration') in ('any', 'long', 'medium', 'short'):
            params['videoDuration'] = kw['duration']
        response = await self.fetch(
            ids['provider_id'], '/search', params=params)
        search_result = tornado.escape.json_decode(response.body)
        video_ids = [i['id']['videoId'] for i in search_result['items']]

        futures = []
        for i, j in chunk_range(len(video_ids)):
            tracks = self.mread(ids, {'ids': video_ids[i: j]}, fields=fields)
            futures.append(tracks)

        entities = await tornado.gen.multi(futures)
        return list(itertools.chain(*entities))
