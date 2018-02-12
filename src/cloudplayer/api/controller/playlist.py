"""
    cloudplayer.api.controller.playlist
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
from  sqlalchemy.sql.expression import func
import tornado.gen

from cloudplayer.api.model.playlist import Playlist
from cloudplayer.api.policy import Owned
import cloudplayer.api.controller


class PlaylistController(cloudplayer.api.controller.Controller):

    __model__ = Playlist
    __policies__ = [Owned]

    @tornado.gen.coroutine
    def read(self, ids):
        if ids['id'] == 'random':
            random = self.db.query(
                self.__model__).order_by(func.random()).first()
            if random:
                ids['id'] = random.id
        entity = self.policy.read(self.__model__, ids)
        return entity
