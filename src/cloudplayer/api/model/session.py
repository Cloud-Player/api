"""
    cloudplayer.api.model.session
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import functools

import sqlalchemy as sql
import sqlalchemy.orm as orm

from cloudplayer.api.access import Allow, Create, Deny, Fields, Owner, Read
from cloudplayer.api.model import Base
from cloudplayer.api.util import gen_token


class Session(Base):

    __acl__ = (
        Allow(Owner, Create, Fields(
            'account_id',
            'account_provider_id',
            'system',
            'browser',
            'screen'
        )),
        Allow(Owner, Read, Fields()),
        Deny()
    )
    __table_args__ = (
        sql.PrimaryKeyConstraint(
            'id'),
        sql.ForeignKeyConstraint(
            ['account_id', 'account_provider_id'],
            ['account.id', 'account.provider_id'])
    )

    id = sql.Column(sql.String(64), default=functools.partial(gen_token, 64))

    account_id = sql.Column(sql.String(32), nullable=False)
    account_provider_id = sql.Column(sql.String(16), nullable=False)
    account = orm.relation(
        'Account',
        back_populates='sessions',
        uselist=False,
        single_parent=True)
    parent = orm.synonym('account')

    system = sql.Column(sql.String(64), nullable=False)
    browser = sql.Column(sql.String(64), nullable=False)
    screen = sql.Column(sql.String(32), nullable=False)
