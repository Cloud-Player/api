"""
    cloudplayer.api.model.account
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import sqlalchemy as sql
import sqlalchemy.orm as orm

from cloudplayer.api.access import (Allow, Deny, Everyone, Fields, Owner,
                                    Query, Read, Update)
from cloudplayer.api.model import Base


class Account(Base):

    __acl__ = (
        Allow(Owner, Read, Fields(
            'id',
            'provider_id',
            'user_id',
            'connected',
            'favourite_id',
            'image.id',
            'image.small',
            'image.medium',
            'image.large',
            'title',
            'created',
            'updated'
        )),
        Allow(Owner, Update, Fields(
            'image',
            'title'
        )),
        Allow(Everyone, Read, Fields(
            'id',
            'provider_id',
            'image.id',
            'image.small',
            'image.medium',
            'image.large',
            'title'
        )),
        Allow(Everyone, Query, Fields(
            'provider_id',
            'title'
        )),
        Deny()
    )
    __fields__ = (
        'id',
        'provider_id',
        'user_id',
        'connected',
        'favourite_id',
        'image_id',
        'title',
        'created',
        'updated'
    )
    __channel__ = (
        'acocunt.{provider_id}.{id}',
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
            ['image.id'])
    )

    id = sql.Column(sql.String(32))
    account_id = orm.synonym('id')

    provider_id = sql.Column(sql.String(16), nullable=False)
    provider = orm.relation(
        'Provider',
        cascade=None,
        uselist=False,
        viewonly=True)
    account_provider_id = orm.synonym('provider_id')

    user_id = sql.Column(sql.Integer, nullable=False)
    user = orm.relation(
        'User',
        back_populates='accounts',
        uselist=False,
        viewonly=True)
    parent = orm.synonym('user')

    image_id = sql.Column(sql.Integer)
    image = orm.relation(
        'Image',
        cascade='all, delete-orphan',
        single_parent=True,
        uselist=False)

    @property
    def favourite_id(self):
        if self.favourite:
            return self.favourite.id

    favourite = orm.relation(
        'Favourite',
        back_populates='account',
        cascade='all, delete-orphan',
        single_parent=True,
        uselist=False)

    playlists = orm.relation(
        'Playlist',
        back_populates='account',
        cascade='all, delete-orphan',
        single_parent=True)

    title = sql.Column('title', sql.Unicode(64))

    access_token = sql.Column(sql.String(256))
    refresh_token = sql.Column(sql.String(256))
    token_expiration = sql.Column(sql.DateTime())

    @property
    def connected(self):
        return self.provider_id == 'cloudplayer' or all([
            self.access_token, self.refresh_token])
