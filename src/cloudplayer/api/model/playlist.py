"""
    cloudplayer.api.model.playlist
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import sqlalchemy as sql
import sqlalchemy.orm as orm
from sqlalchemy.ext.declarative import declared_attr

from cloudplayer.api.access import (Allow, Create, Delete, Deny, Fields, Owner,
                                    Query, Read, Update)
from cloudplayer.api.model import Base
from cloudplayer.api.model.tracklist import TracklistMixin


class Playlist(TracklistMixin, Base):

    __acl__ = (
        Allow(Owner, Create, Fields(
            'provider_id',
            'account_id',
            'account_provider_id',
        )),
        Allow(Owner, Read, Fields(
            'id',
            'provider_id',
            'account_id',
            'account_provider_id',
            'description',
            'follower_count',
            'image.id',
            'image.small',
            'image.medium',
            'image.large',
            'items',
            'public',
            'title',
            'created',
            'updated'
        )),
        Allow(Owner, Update, Fields(
            'description',
            'title'
        )),
        Allow(Owner, Delete),
        Allow(Owner, Query, Fields(
            'account_id',
            'account_provider_id',
            'provider_id'
        )),
        Deny()
    )

    @declared_attr
    def __table_args__(cls):
        return super().__table_args__ + (
            sql.ForeignKeyConstraint(
                ['image_id'],
                ['image.id']),
        )

    account = orm.relation(
        'Account',
        back_populates='playlists',
        viewonly=True)
    parent = orm.synonym('account')

    items = orm.relation(
        'PlaylistItem',
        cascade='all, delete-orphan',
        order_by='PlaylistItem.rank',
        single_parent=True)

    description = sql.Column(sql.Unicode(5120), nullable=True)
    follower_count = sql.Column(sql.Integer, default=0)
    public = sql.Column(sql.Boolean, default=False)
    title = sql.Column(sql.Unicode(256), nullable=False)

    image_id = sql.Column(sql.Integer)
    image = orm.relation(
        'Image',
        cascade='all, delete-orphan',
        single_parent=True,
        uselist=False)
