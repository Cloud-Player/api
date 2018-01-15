"""
    cloudplayer.api.model.favourite_item
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
import sqlalchemy as sql
import sqlalchemy.orm as orm

from cloudplayer.api.model import Base
from cloudplayer.api.model.tracklist_item import TracklistItemMixin


class FavouriteItem(TracklistItemMixin, Base):

    __fields__ = [
        'id',
        'track_provider_id',
        'track_id'
    ]
    __filters__ = [
        'favourite_id'
    ]
    __mutable__ = []
    __public__ = __fields__
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

    favourite_provider_id = sql.Column(sql.String(16), nullable=False)
    favourite_id = sql.Column(sql.String(96), nullable=False)
    favourite = orm.relationship('Favourite', back_populates='items')
