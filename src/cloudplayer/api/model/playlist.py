"""
    cloudplayer.api.model.playlist
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import sqlalchemy as sql
import sqlalchemy.orm as orm

from cloudplayer.api.model import Base
from cloudplayer.api.model.tracklist import TracklistMixin


class Playlist(TracklistMixin, Base):

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

    account = orm.relationship(
        'Account', back_populates='playlists', viewonly=True)

    title = sql.Column(sql.String(256), nullable=False)

    items = orm.relationship('PlaylistItem')
