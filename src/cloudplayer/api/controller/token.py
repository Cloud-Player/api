"""
    cloudplayer.api.controller.token
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import datetime

from cloudplayer.api.access import Available
from cloudplayer.api.controller import Controller, ControllerException
from cloudplayer.api.model.token import Token


class TokenController(Controller):

    __model__ = Token

    async def read(self, ids, fields=Available):
        threshold = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
        query = self.db.query(
            self.__model__).filter_by(**ids).filter(Token.created > threshold)
        entity = query.first()
        if not entity:
            raise ControllerException(404, 'token not found')
        account = self.get_account(entity.provider_id)
        self.policy.grant_read(account, entity, fields)
        if entity.claimed:
            self.current_user.clear()
            self.current_user['user_id'] = entity.account.user_id
            for a in entity.account.user.accounts:
                self.current_user[a.provider_id] = a.id
            entity.account_id = None
            entity.account_provider_id = None
            self.db.commit()
        return entity

    async def update(self, ids, kw, fields=Available):
        token = {
            'id': ids['id'],
            'claimed': True,
            'account_id': self.current_user['cloudplayer'],
            'account_provider_id': 'cloudplayer'}
        if kw != token:
            raise ControllerException(404, 'invalid update')
        return await super().update(ids, kw, fields=fields)
