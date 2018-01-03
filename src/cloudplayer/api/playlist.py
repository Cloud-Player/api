"""
    cloudplayer.api.playlist
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
import tornado.gen
import tornado.web

from cloudplayer.api.model import Playlist
import cloudplayer.api.handler


class Entity(cloudplayer.api.handler.HTTPHandler):

    __model__ = Playlist

    @tornado.gen.coroutine
    def get(self, id):
        playlist = self.db.query(
            Playlist
        ).filter(
            Playlist.id == id
        ).one_or_none()

        yield self.write(playlist)


class Collection(cloudplayer.api.handler.HTTPHandler):

    __model__ = Playlist

    @tornado.gen.coroutine
    def get(self):
        provider = self.get_argument('provider_id')
        if provider == 'youtube':
            playlists = yield self.get_youtube()
        elif provider == 'soundcloud':
            playlists = yield self.get_souncloud()
        elif provider == 'cloudplayer':
            playlists = yield self.get_cloudplayer()
        else:
            raise tornado.web.HTTPError(400, 'invalid provider_id')
        yield self.write(playlists)

    @tornado.gen.coroutine
    def get_youtube(self):
        return

    @tornado.gen.coroutine
    def get_souncloud(self):
        return

    @tornado.gen.coroutine
    def get_cloudplayer(self):
        query = self.db.query(Playlist)
        accountId = self.get_argument('account_id', None)
        if accountId:
            query = query.filter(Playlist.account_id == accountId)
        return query.all()

    @tornado.gen.coroutine
    def post(self):
        entity = self.body_json()
        if not isinstance(entity, dict):
            raise tornado.web.HTTPError(400, 'invalid playlist format')
        elif 'title' not in entity:
            raise tornado.web.HTTPError(400, 'playlist missing title')
        playlist = Playlist(
            title=entity['title'],
            public=entity.get('public', False),
            account_id=self.current_user['cloudplayer'],
            account_provider='cloudplayer')
        self.db.add(playlist)
        self.db.commit()
        self.write(playlist)
