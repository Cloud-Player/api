"""
    cloudplayer.api.controller.playlist_item
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import tornado.gen

from cloudplayer.api.controller import Controller, ControllerException
from cloudplayer.api.model.playlist import Playlist
from cloudplayer.api.model.playlist_item import PlaylistItem


class PlaylistItemController(Controller):

    __model__ = PlaylistItem

    @tornado.gen.coroutine
    def query(self, ids, kw):
        # TODO: Resolve this workaround with dynamic parent resolution
        playlist = self.db.query(Playlist).get(
            (ids.pop('playlist_id'), ids.pop('playlist_provider_id')))
        kw.pop('playlist_id', None)
        kw.pop('playlist_provider_id', None)
        if not playlist:
            raise ControllerException(404, 'playlist not found')
        kw['playlist'] = playlist
        query = yield super().query(ids, kw)
        return query.order_by(PlaylistItem.rank)
