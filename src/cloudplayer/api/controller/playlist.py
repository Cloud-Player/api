"""
    cloudplayer.api.controller.playlist
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import tornado.gen
from sqlalchemy.sql.expression import func

from cloudplayer.api.access import Available
from cloudplayer.api.controller import Controller
from cloudplayer.api.model.playlist import Playlist


class PlaylistController(Controller):

    __model__ = Playlist

    @tornado.gen.coroutine
    def read(self, ids, fields=Available):
        if ids['id'] == 'random':
            provider_id = ids['provider_id']
            account = self.accounts.get(provider_id)
            kw = dict(
                account_id=account.id,
                account_provider_id=account.provider_id,
                provider_id=provider_id)
            self.policy.grant_query(account, self.__model__, kw)
            ids = dict(
                provider_id=provider_id)
            query = yield self.query(ids, kw)
            random = query.order_by(func.random()).first()
            if random:
                ids['id'] = random.id
        entity = yield super().read(ids, fields=fields)
        return entity
