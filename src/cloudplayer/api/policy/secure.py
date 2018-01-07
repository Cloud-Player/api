"""
    cloudplayer.api.policy.secure
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
import tornado.options as opt

from cloudplayer.api.policy import Mixin, PolicyViolation


class Secure(Mixin):

    def check_mine(self, entity):
        try:
            return self.current_user[self.provider_id] == self.account_id
        except (TypeError, KeyError):
            return False

    def read(self, query, *ids):
        entity = super().read(query, *ids)
        if not self.check_mine(entity):
            raise PolicyViolation('entity access denied')
        return entity

    def update(self, entity, **kw):
        if not self.check_mine(entity):
            raise PolicyViolation('entity update denied')
        super().update(entity, **kw)

    def delete(self, entity, **kw):
        if not self.check_mine(entity):
            raise PolicyViolation('entity deletion denied')
        super().delete(entity, **kw)

    def query(self, model, **kw):
        query = self.db.query(model)
        for field, value in kw:
            expression = getattr(model, field) == value
            query = query.filter(expression)
        for provider_id, account_id in self.current_user:
            if provider_id in opt.options.providers:
                # TODO: Formulate provider/account_id filter
                pass
        query = query.filter()
        return query
