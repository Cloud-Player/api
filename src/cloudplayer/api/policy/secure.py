"""
    cloudplayer.api.policy.secure
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
import sqlalchemy as sql
import tornado.options as opt

from cloudplayer.api.policy import Mixin, PolicyViolation


class Secure(Mixin):

    def read(self, model, ids):
        entity = super().read(model, ids)
        if entity and not self._is_mine(entity):
            entity = None
        return entity

    def update(self, model, entity, **kw):
        if entity and not self._is_mine(entity):
            entity = None
        super().update(model, entity, **kw)

    def delete(self, entity, **kw):
        if entity and not self._is_mine(entity):
            entity = None
        super().delete(entity, **kw)

    def query(self, model, **kw):
        query = self.db.query(model)
        for field, value in kw.items():
            expression = getattr(model, field) == value
            query = query.filter(expression)
        clauses = []
        for provider_id in opt.options.providers:
            if self.current_user.get(provider_id):
                credentials = sql.and_(
                    model.account_id == self.current_user[provider_id],
                    model.account_provider_id == provider_id)
                clauses.append(credentials)
        return query.filter(sql.or_(*clauses))
