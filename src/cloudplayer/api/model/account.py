"""
    cloudplayer.api.model.account
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import sqlalchemy as sql
import sqlalchemy.orm as orm

from cloudplayer.api.access import (Allow, Everyone, Fields, Owner,
                                    Query, Read, Update)
from cloudplayer.api.model import Base


class Account(Base):

    __acl__ = (
        Allow(Owner, Read),
        Allow(Owner, Update, Fields(
            'image',
            'title'
        )),
        Allow(Everyone, Read, Fields(
            'id',
            'image',
            'provider_id',
            'title'
        )),
        Allow(Everyone, Query, Fields(
            'provider_id',
            'title'
        ))
    )
    __fields__ = Fields(
        'id',
        'provider_id',
        'user_id',
        'connected',
        'created',
        'updated',
        'favourite',
        'title',
        'image'
    )
    __table_args__ = (
        sql.PrimaryKeyConstraint(
            'id', 'provider_id'),
        sql.ForeignKeyConstraint(
            ['provider_id'],
            ['provider.id']),
        sql.ForeignKeyConstraint(
            ['user_id'],
            ['user.id']),
        sql.ForeignKeyConstraint(
            ['image_id'],
            ['image.id']),
    )

    id = sql.Column(sql.String(32))

    account_id = orm.synonym('id')

    provider_id = sql.Column(sql.String(16), nullable=False)
    provider = orm.relationship('Provider')

    user_id = sql.Column(sql.Integer, nullable=False)
    user = orm.relationship('User', back_populates='accounts')
    parent = orm.synonym('user')

    playlists = orm.relationship('Playlist', back_populates='account')
    favourite = orm.relationship(
        'Favourite', uselist=False, back_populates='account')

    title = sql.Column('title', sql.String(64))
    image_id = sql.Column(sql.Integer)
    image = orm.relationship('Image')

    access_token = sql.Column(sql.String(256))
    refresh_token = sql.Column(sql.String(256))
    token_expiration = sql.Column(sql.DateTime())

    @property
    def connected(self):
        return self.provider_id == 'cloudplayer' or all([
            self.access_token, self.refresh_token])

    def __eq__(self, other):
        if isinstance(other, Account):
            return (
                self.provider_id == other.provider_id and self.id == other.id)
        return super().__eq__(other)
