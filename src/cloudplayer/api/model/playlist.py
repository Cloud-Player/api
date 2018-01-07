"""
    cloudplayer.api.model.playlist
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
import functools

from sqlalchemy.sql import func
import sqlalchemy as sql
import sqlalchemy.orm as orm

from cloudplayer.api.model import Base
import cloudplayer.api.util


class Playlist(Base):

    __tablename__ = 'playlist'
    __fields__ = [
        'id',
        'account_id',
        'provider_id',
        'title',
        'public',
        'follower_count',
        'items'
    ]
    __filters__ = [
        'account_id',
        'provider_id',
        'title',
        'public',
        'follower_count'
    ]
    __mutable__ = [
        'title',
        'public'
    ]
    __public__ = __fields__
    __table_args__ = (
        sql.PrimaryKeyConstraint(
            'id', 'provider_id'),
        sql.ForeignKeyConstraint(
            ['provider_id'],
            ['provider.id']),
        sql.ForeignKeyConstraint(
            ['account_id', 'provider_id'],
            ['account.id', 'account.provider_id'])
    )

    id = sql.Column(sql.String(96), default=functools.partial(
        cloudplayer.api.util.gen_token, 16))

    provider_id = sql.Column(sql.String(16))
    provider = orm.relationship('Provider')

    account_provider_id = orm.synonym('provider_id')
    account_id = sql.Column(sql.String(32), nullable=False)
    account = orm.relationship(
        'Account', back_populates='playlists', viewonly=True)

    title = sql.Column(sql.String(512), nullable=False)
    public = sql.Column(sql.Boolean, default=False)
    follower_count = sql.Column(sql.Integer, default=0)

    items = orm.relationship('PlaylistItem')

    created = sql.Column(
        sql.DateTime(timezone=True), server_default=func.now())
    updated = sql.Column(
        sql.DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now())
