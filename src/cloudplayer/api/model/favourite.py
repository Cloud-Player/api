"""
    cloudplayer.api.model.favourite
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import sqlalchemy.orm as orm

from cloudplayer.api.access import Allow, Fields, Owner, Read
from cloudplayer.api.model import Base
from cloudplayer.api.model.tracklist import TracklistMixin


class Favourite(TracklistMixin, Base):

    __acl__ = (
        Allow(Owner, Read, Fields(
            'id',
            'provider_id',
            'account_id',
            'account_provider_id',
            'items'
        )),
    )

    account = orm.relation(
        'Account',
        back_populates='favourite',
        viewonly=True)

    items = orm.relation(
        'FavouriteItem',
        cascade='all, delete-orphan',
        order_by='FavouriteItem.created',
        single_parent=True)
