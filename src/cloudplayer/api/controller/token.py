"""
    cloudplayer.api.controller.token
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import datetime

import tornado.gen
import tornado.options as opt

from cloudplayer.api.model.token import Token
import cloudplayer.api.controller


class TokenController(cloudplayer.api.controller.Controller):

    __model__ = Token

    @tornado.gen.coroutine
    def create(self, ids, **kw):
        entity = yield super().create({})
        return entity

    @tornado.gen.coroutine
    def read(self, ids):
        query = yield self.query(ids)
        entity = query.one_or_none()
        if entity and entity.claimed:
            self.current_user['user_id'] = entity.account.user_id
            for p in opt.options['providers']:
                self.current_user[p] = None
            for a in entity.account.user.accounts:
                self.current_user[a.provider_id] = a.id
            entity.account_id = None
            entity.account_provider_id = None
            self.db.commit()
        return entity

    @tornado.gen.coroutine
    def update(self, ids, **kw):
        entity = yield super().update(
            ids,
            claimed=True,
            account_id=self.current_user['cloudplayer'],
            account_provider_id='cloudplayer')
        return entity

    @tornado.gen.coroutine
    def query(self, ids, **kw):
        query = yield super().query(ids, **kw)
        threshold = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
        return query.filter(Token.created > threshold)
