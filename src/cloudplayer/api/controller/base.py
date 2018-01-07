"""
    cloudplayer.api.controller.base
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
from sqlalchemy.inspection import inspect

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

    def create(self, ids, **kw):
        kw = self._merge_ids_into_kw(ids, **kw)
        entity = self.__model__(**kw)
        self.policy.create(entity)
        self.db.commit()
        return entity

    def read(self, ids):
        entity = self.policy.read(self.__model__, ids)
        return entity

    def update(self, ids, **kw):
        kw = self._merge_ids_into_kw(ids, **kw)
        entity = self.read(ids)
        self.policy.update(entity, **kw)
        self.db.commit()
        return entity

    def delete(self, ids):
        entity = self.read(ids)
        self.policy.delete(entity)
        self.db.commit()

    def query(self, ids, **kw):
        kw = self._merge_ids_into_kw(ids, **kw)
        return self.policy.query(self.__model__, **kw)

    def search(self, ids, **kw):
        return self.query(ids, **kw).all()

    def count(self, ids, **kw):
        return self.query(ids, **kw).count()
