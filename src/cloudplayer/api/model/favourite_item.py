"""
    cloudplayer.api.model.favourite_item
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import sqlalchemy as sql
import sqlalchemy.orm as orm

from cloudplayer.api.access import (Allow, Create, Delete, Fields, Owner,
                                    Parent, Query, Read)
from cloudplayer.api.model import Base
from cloudplayer.api.model.tracklist_item import TracklistItemMixin


class FavouriteItem(TracklistItemMixin, Base):

    __acl__ = (
        Allow(Parent, Create, Fields(
            'account_id',
            'account_provider_id',
            'track_provider_id',
            'track_id'
        )),
        Allow(Owner, Read, Fields(
            'id',
            'track_provider_id',
            'track_id'
        )),
        Allow(Owner, Delete),
        Allow(Owner, Query, Fields(
            'favourite_id'
        ))
    )
    __table_args__ = (
        sql.PrimaryKeyConstraint(
            'id'),
        sql.ForeignKeyConstraint(
            ['favourite_provider_id', 'favourite_id'],
            ['favourite.provider_id', 'favourite.id']),
        sql.ForeignKeyConstraint(
            ['account_id', 'account_provider_id'],
            ['account.id', 'account.provider_id']),
        sql.ForeignKeyConstraint(
            ['track_provider_id'],
            ['provider.id'])
    )

    provider_id = orm.synonym('favourite_provider_id')

    favourite_id = sql.Column(sql.String(96), nullable=False)
    favourite_provider_id = sql.Column(sql.String(16), nullable=False)
    favourite = orm.relation(
        'Favourite',
        back_populates='items',
        viewonly=True)
    parent = orm.synonym('favourite')
