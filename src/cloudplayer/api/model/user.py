"""
    cloudplayer.api.model.user
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import sqlalchemy as sql
import sqlalchemy.orm as orm

from cloudplayer.api.access import Allow, Child, Deny, Fields, Read
from cloudplayer.api.model import Base


class User(Base):

    __acl__ = (
        Allow(Child, Read),
        Deny()
    )
    __fields__ = Fields(
        'id',
        'accounts',
        'created',
        'updated'
    )
    __table_args__ = (
        sql.PrimaryKeyConstraint(
            'id'),
    )

    id = sql.Column(sql.Integer)
    provider_id = 'cloudplayer'

    accounts = orm.relationship('Account', back_populates='user')
    children = orm.synonym('accounts')
