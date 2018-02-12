"""
    cloudplayer.api.model.favourite
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import sqlalchemy.orm as orm

from cloudplayer.api.model import Base
from cloudplayer.api.model.tracklist import TracklistMixin


class Favourite(TracklistMixin, Base):

    __fields__ = [
        'id',
        'account_id',
        'provider_id',
        'public',
        'items'
    ]
    __filters__ = [
        'account_id',
        'provider_id',
        'public',
        'follower_count'
    ]
    __mutable__ = []
    __public__ = __fields__

    account = orm.relationship(
        'Account', back_populates='favourite', viewonly=True)

    items = orm.relationship('FavouriteItem')
