"""
    cloudplayer.api.model.playlist
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import sqlalchemy as sql
import sqlalchemy.orm as orm

from cloudplayer.api.access import (Allow, Create, Delete, Deny, Everyone,
                                    Fields, Owner, Query, Read, Update)
from cloudplayer.api.model import Base
from cloudplayer.api.model.tracklist import TracklistMixin


class Playlist(TracklistMixin, Base):

    __acl__ = (
        Allow(Owner, Read),
        Allow(Owner, Update, Fields(
            'title'
        )),
        Allow(Owner, Delete),
        Allow(Owner, Query, Fields(
            'account_id',
            'provider_id',
            'title'
        )),
        Allow(Everyone, Create),
        Deny()
    )
    __fields__ = Fields(
        'id',
        'account_id',
        'provider_id',
        'title',
        'public',
        'follower_count',
        'items'
    )

    account = orm.relationship(
        'Account', back_populates='playlists', viewonly=True)

    title = sql.Column(sql.String(256), nullable=False)

    items = orm.relationship('PlaylistItem')
