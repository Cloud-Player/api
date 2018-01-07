"""
    cloudplayer.api.model.playlist_item
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
from sqlalchemy.sql import func
import sqlalchemy as sql
import sqlalchemy.orm as orm

from cloudplayer.api.model import Base


class PlaylistItem(Base):

    __tablename__ = 'playlist_item'
    __fields__ = [
        'id',
        'rank',
        'track'
    ]
    __filters__ = [
        'rank',
        'playlist_id'
    ]
    __mutable__ = [
        'rank'
    ]
    __public__ = __fields__
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
            ['track_provider_id', 'track_id'],
            ['track.provider_id', 'track.id'])
    )

    id = sql.Column(sql.Integer)
    rank = sql.Column(sql.String(128), nullable=False)

    playlist_provider_id = sql.Column(sql.String(16), nullable=False)
    playlist_id = sql.Column(sql.String(96), nullable=False)
    playlist = orm.relationship('Playlist', back_populates='items')

    account_provider_id = sql.Column(sql.String(16), nullable=False)
    account_id = sql.Column(sql.String(32), nullable=False)
    account = orm.relationship('Account')

    track_provider_id = sql.Column(sql.String(16), nullable=False)
    track_id = sql.Column(sql.String(128), nullable=False)
    track = orm.relationship('Track')

    created = sql.Column(
        sql.DateTime(timezone=True), server_default=func.now())
    updated = sql.Column(
        sql.DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now())
