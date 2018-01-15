"""
    cloudplayer.api.policy.owned
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.policy import Mixin, PolicyViolation


class Owned(Mixin):

    def create(self, entity):
        if not entity.account_provider_id:
            provider_id = entity.__table__.c.account_provider_id.default.arg
            entity.account_provider_id = provider_id
        if not self.current_user.get(entity.account_provider_id):
            raise PolicyViolation('entity creation denied')
        entity.account_id = self.current_user[entity.account_provider_id]
        super().create(entity)
