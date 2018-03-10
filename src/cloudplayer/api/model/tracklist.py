"""
    cloudplayer.api.model.tracklist
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import functools

import sqlalchemy as sql
import sqlalchemy.orm as orm
from sqlalchemy.ext.declarative import declared_attr

import cloudplayer.api.util


class TracklistMixin(object):

    @declared_attr
    def __table_args__(cls):
        return (
            sql.PrimaryKeyConstraint(
                'id', 'provider_id'),
            sql.ForeignKeyConstraint(
                ['provider_id'],
                ['provider.id']),
            sql.ForeignKeyConstraint(
                ['account_id', 'account_provider_id'],
                ['account.id', 'account.provider_id'])
        )

    id = sql.Column(sql.String(96), default=functools.partial(
        cloudplayer.api.util.gen_token, 16))

    provider_id = sql.Column(sql.String(16), default='cloudplayer')

    @declared_attr
    def provider(cls):
        return orm.relationship('Provider')

    account_provider_id = sql.Column(sql.String(16), nullable=False)
    account_id = sql.Column(sql.String(32), nullable=False)

    public = sql.Column(sql.Boolean, default=False)
    follower_count = sql.Column(sql.Integer, default=0)
