"""
    cloudplayer.api.model.user
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import sqlalchemy as sql
import sqlalchemy.orm as orm

from cloudplayer.api.access import Allow, Child, Fields, Read
from cloudplayer.api.model import Base


class User(Base):

    __acl__ = (
        Allow(Child, Read, Fields(
            'id',
            'provider_id',
            'accounts.id',
            'accounts.provider_id',
            'accounts.connected',
            'accounts.favourite_id',
            'accounts.image',
            'accounts.title',
            'created',
            'updated'
        )),
    )
    __table_args__ = (
        sql.PrimaryKeyConstraint(
            'id'),
    )

    id = sql.Column(sql.Integer)
    provider_id = 'cloudplayer'

    accounts = orm.relation(
        'Account',
        back_populates='user',
        uselist=True,
        single_parent=True,
        cascade='all, delete-orphan')
    children = orm.synonym('accounts')
