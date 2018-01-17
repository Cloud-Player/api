"""
    cloudplayer.api.model.token
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
import functools

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import func
import sqlalchemy as sql
import sqlalchemy.orm as orm

from cloudplayer.api.model import Base
from cloudplayer.api.util import gen_token


class Token(Base):

    __fields__ = [
        'id',
        'claimed'
    ]
    __filters__ = []
    __mutable__ = [
        'claimed'
    ]
    __public__ = []
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

    @declared_attr
    def account(cls):
        return orm.relationship('Account')
