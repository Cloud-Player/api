"""
    cloudplayer.api.controller.base
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import tornado.gen
import tornado.options as opt

from cloudplayer.api import APIException
from cloudplayer.api.access import Available, Policy


class ControllerException(APIException):

    def __init__(self, status_code=400, log_message='controller exception'):
        super().__init__(status_code, log_message)


class Controller(object):

    __model__ = NotImplemented

    def __init__(self, db, current_user=None):
        self.db = db
        self.current_user = current_user
        self.policy = Policy(db, current_user)

    @staticmethod
    def _merge_ids_with_kw(ids, kw):
        # XXX: This exposes entity existence
        params = kw.copy()
        for field, value in ids.items():
            if field in params and params[field] != value:
                raise ControllerException(400, 'mismatch on {}'.format(field))
            params[field] = value
        return params

    @staticmethod
    def _eject_ids_from_kw(ids, kw):
        # XXX: This exposes entity existence
        params = kw.copy()
        for field, value in ids.items():
            if field in params:
                if params[field] == value:
                    del params[field]
                else:
                    raise ControllerException(
                        400, 'mismatch on {}'.format(field))
        return params

    @tornado.gen.coroutine
    def fetch(self, provider_id, path, **kw):
        # TODO: Can authed fetching be generalized
        from cloudplayer.api.controller.auth import create_controller
        controller = create_controller(
            provider_id, self.db, self.current_user)
        response = yield controller.fetch(path, **kw)
        return response

    @property
    def accounts(self):
        # TODO: Move detached accounts to current_user
        from sqlalchemy.orm.session import make_transient_to_detached
        from cloudplayer.api.model.account import Account
        dict_ = {}
        for provider_id in opt.options['providers']:
            account = Account(
                id=self.current_user[provider_id],
                provider_id=provider_id)
            make_transient_to_detached(account)
            account = self.db.merge(account, load=False)
            dict_[provider_id] = account
        return dict_

    @tornado.gen.coroutine
    def create(self, ids, kw, fields=Available):
        params = self._merge_ids_with_kw(ids, kw)
        entity = self.__model__(**params)
        account = self.accounts.get(entity.provider_id)
        self.policy.grant_create(account, entity, params.keys())
        self.db.add(entity)
        self.db.commit()
        self.policy.grant_read(account, entity, fields)
        return entity

    @tornado.gen.coroutine
    def read(self, ids, fields=Available):
        entity = self.db.query(self.__model__).filter_by(**ids).one_or_none()
        if not entity:
            raise ControllerException(404, 'not found')
        account = self.accounts.get(entity.provider_id)
        self.policy.grant_read(account, entity, fields)
        return entity

    @tornado.gen.coroutine
    def update(self, ids, kw, fields=Available):
        entity = self.db.query(self.__model__).filter_by(**ids).one_or_none()
        if not entity:
            raise ControllerException(404, 'not found')
        account = self.accounts.get(entity.provider_id)
        self.policy.grant_read(account, entity, fields)
        params = self._eject_ids_from_kw(ids, kw)
        self.policy.grant_update(account, entity, params)
        self.db.query(self.__model__).filter_by(**ids).update(params)
        self.db.commit()
        return entity

    @tornado.gen.coroutine
    def delete(self, ids):
        entity = self.db.query(self.__model__).filter_by(**ids).one_or_none()
        if not entity:
            raise ControllerException(404, 'not found')
        account = self.accounts.get(entity.provider_id)
        self.policy.grant_delete(account, entity)
        self.db.delete(entity)
        self.db.commit()

    @tornado.gen.coroutine
    def query(self, ids, kw):
        account = self.accounts.get(ids['provider_id'])
        self.policy.grant_query(account, self.__model__, kw)
        params = self._merge_ids_with_kw(ids, kw)
        query = self.db.query(self.__model__)
        for field, value in params.items():
            expression = getattr(self.__model__, field) == value
            query = query.filter(expression)
        return query

    @tornado.gen.coroutine
    def search(self, ids, kw, fields=Available):
        query = yield self.query(ids, kw)
        entities = query.all()
        account = self.accounts.get(ids['provider_id'])
        for entity in entities:  # TODO: Find a better way
            self.policy.grant_read(account, entity, fields)
        return entities
