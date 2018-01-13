"""
    cloudplayer.api.model.favourites_item
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
import sqlalchemy as sql
import sqlalchemy.orm as orm

from cloudplayer.api.model import Base
from cloudplayer.api.model.tracklist_item import TracklistItemMixin


class FavouritesItem(TracklistItemMixin, Base):

    __fields__ = [
        'id',
        'track_provider_id',
        'track_id'
    ]
    __filters__ = [
        'favourites_id'
    ]
    __mutable__ = []
    __public__ = __fields__
    __table_args__ = (
        sql.PrimaryKeyConstraint(
            'id'),
        sql.ForeignKeyConstraint(
            ['favourites_provider_id', 'favourites_id'],
            ['favourites.provider_id', 'favourites.id']),
        sql.ForeignKeyConstraint(
            ['account_id', 'account_provider_id'],
            ['account.id', 'account.provider_id']),
        sql.ForeignKeyConstraint(
            ['track_provider_id'],
            ['provider.id'])
    )

    favourites_provider_id = sql.Column(sql.String(16), nullable=False)
    favourites_id = sql.Column(sql.String(96), nullable=False)
    favourites = orm.relationship('Favourites', back_populates='items')
