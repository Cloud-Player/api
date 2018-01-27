"""
    cloudplayer.api.controller.base
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
from sqlalchemy.inspection import inspect
import tornado.gen

from cloudplayer.api.controller.auth import create_controller
import cloudplayer.api.policy


class Controller(object):

    __model__ = NotImplemented
    __policies__ = NotImplemented

    def __init__(self, db, current_user=None):
        self.db = db
        self.current_user = current_user
        factory = cloudplayer.api.policy.PolicyFactory(self.__policies__)
        self.policy = factory(db, current_user)

    @staticmethod
    def _merge_ids_into_kw(ids, **kw):
        for field, value in ids.items():
            if field in kw and kw[field] != value:
                raise ValueError('mismatch of %s', field)
            kw[field] = value
        return kw

    @tornado.gen.coroutine
    def fetch(self, provider_id, path, **kw):
        controller = create_controller(
            provider_id, self.db, self.current_user)
        response = yield controller.fetch(path, **kw)
        return response

    @tornado.gen.coroutine
    def create(self, ids, **kw):
        kw = self._merge_ids_into_kw(ids, **kw)
        entity = self.__model__(**kw)
        self.policy.create(entity)
        self.db.commit()
        return entity

    @tornado.gen.coroutine
    def read(self, ids):
        entity = self.policy.read(self.__model__, ids)
        return entity

    @tornado.gen.coroutine
    def update(self, ids, **kw):
        kw = self._merge_ids_into_kw(ids, **kw)
        entity = yield self.read(ids)
        self.policy.update(self.__model__, entity, **kw)
        self.db.commit()
        return entity

    @tornado.gen.coroutine
    def delete(self, ids):
        entity = yield self.read(ids)
        self.policy.delete(entity)
        self.db.commit()

    @tornado.gen.coroutine
    def query(self, ids, **kw):
        kw = self._merge_ids_into_kw(ids, **kw)
        return self.policy.query(self.__model__, **kw)

    @tornado.gen.coroutine
    def search(self, ids, **kw):
        query = yield self.query(ids, **kw)
        return query.all()

    @tornado.gen.coroutine
    def count(self, ids, **kw):
        query = yield self.query(ids, **kw)
        return query.count()
