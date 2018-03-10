"""
    cloudplayer.api.model.provider
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import sqlalchemy as sql
import sqlalchemy.orm as orm
import tornado.options as opt

from cloudplayer.api.access import Allow, Everyone, Fields, Query, Read
from cloudplayer.api.model import Base


class Provider(Base):

    __acl__ = (
        Allow(Everyone, Read, Fields(
            'id',
            'client_id'
        )),
        Allow(Everyone, Query, Fields('id'))
    )
    __table_args__ = (
        sql.PrimaryKeyConstraint(
            'id'),
    )

    id = sql.Column(sql.String(12))

    provider_id = orm.synonym('id')

    @property
    def client_id(self):
        if self.id in opt.options['providers']:
            return opt.options[self.id]['api_key']
