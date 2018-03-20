"""
    cloudplayer.api.model.playlist_item
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import sqlalchemy as sql
import sqlalchemy.orm as orm

from cloudplayer.api.access import (Allow, Create, Delete, Deny, Fields, Owner,
                                    Parent, Query, Read, Update)
from cloudplayer.api.model import Base
from cloudplayer.api.model.tracklist_item import TracklistItemMixin


class PlaylistItem(TracklistItemMixin, Base):

    __acl__ = (
        Allow(Parent, Create, Fields(
            'playlist_id',
            'playlist_provider_id',
            'rank',
            'track_provider_id',
            'track_id'
        )),
        Allow(Owner, Read, Fields(
            'id',
            'playlist_id',
            'playlist_provider_id',
            'rank',
            'track_provider_id',
            'track_id',
            'created',
            'updated'
        )),
        Allow(Owner, Update, Fields(
            'rank'
        )),
        Allow(Owner, Delete),
        Allow(Owner, Query, Fields(
            'playlist_id'
        )),
        Deny()
    )
    __table_args__ = (
        sql.PrimaryKeyConstraint(
            'id'),
        sql.ForeignKeyConstraint(
            ['playlist_provider_id', 'playlist_id'],
            ['playlist.provider_id', 'playlist.id']),
        sql.ForeignKeyConstraint(
            ['account_id', 'account_provider_id'],
            ['account.id', 'account.provider_id']),
        sql.ForeignKeyConstraint(
            ['track_provider_id'],
            ['provider.id'])
    )

    provider_id = orm.synonym('playlist_provider_id')

    rank = sql.Column(sql.String(128), nullable=False)

    playlist_id = sql.Column(sql.String(96), nullable=False)
    playlist_provider_id = sql.Column(sql.String(16), nullable=False)
    playlist = orm.relation(
        'Playlist',
        back_populates='items')
    parent = orm.synonym('playlist')
