"""
    cloudplayer.api.model.token
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import functools

import sqlalchemy as sql
import sqlalchemy.orm as orm

from cloudplayer.api.access import (Allow, Create, Everyone, Fields, Read,
                                    Update)
from cloudplayer.api.model import Base
from cloudplayer.api.util import gen_token


class Token(Base):

    __acl__ = (
        Allow(Everyone, Create),
        Allow(Everyone, Update, Fields(
            'claimed',
            'account_id',
            'account_provider_id'
        )),
        Allow(Everyone, Read)
    )
    __fields__ = Fields(
        'id',
        'claimed'
    )
    __table_args__ = (
        sql.PrimaryKeyConstraint(
            'id'),
        sql.ForeignKeyConstraint(
            ['account_id', 'account_provider_id'],
            ['account.id', 'account.provider_id'])
    )

    id = sql.Column(sql.String(16), default=functools.partial(gen_token, 6))

    claimed = sql.Column(sql.Boolean, default=False)

    account_provider_id = sql.Column(sql.String(16))
    account_id = sql.Column(sql.String(32))
    account = orm.relationship('Account')
    parent = orm.synonym('account')
