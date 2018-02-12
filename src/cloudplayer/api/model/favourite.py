"""
    cloudplayer.api.model.favourite
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import sqlalchemy.orm as orm

from cloudplayer.api.access import Allow, Deny, Fields, Owner, Read
from cloudplayer.api.model import Base
from cloudplayer.api.model.tracklist import TracklistMixin


class Favourite(TracklistMixin, Base):

    __acl__ = (
        Allow(Owner, Read),
        Deny()
    )
    __fields__ = Fields(
        'id',
        'account_id',
        'provider_id',
        'public',
        'items'
    )

    account = orm.relationship(
        'Account', back_populates='favourite', viewonly=True)

    items = orm.relationship('FavouriteItem')
