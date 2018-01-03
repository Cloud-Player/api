"""
    cloudplayer.api.model
    ~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
import json
import datetime
import pkg_resources

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import sqlalchemy as sql
import sqlalchemy.ext.declarative
import tornado.options as opt

import cloudplayer.api.auth

Base = sqlalchemy.ext.declarative.declarative_base()


class Encoder(json.JSONEncoder):

    def default(self, obj):
        try:
            return json.JSONEncoder.default(self, obj)
        except:
            if isinstance(obj, Base):
                dict_ = {c: getattr(obj, c) for c in obj.__fields__}
                if 'id' in dict_:  # TODO: There must be a better solution
                    dict_['id'] = str(dict_['id'])
                return dict_
            elif isinstance(obj, datetime.datetime):
                return obj.isoformat()
            elif isinstance(obj, datetime.timedelta):
                return obj.total_seconds()
            return json.JSONEncoder.default(self, obj)


class Account(Base):

    __tablename__ = 'account'
    __fields__ = ['id', 'provider_id', 'user_id', 'created', 'updated',
                  'title', 'image', 'client_id']

    id = sql.Column(sql.String(32), primary_key=True)

    provider_id = sql.Column(
        sql.String(16), sql.ForeignKey('provider.id'), primary_key=True)
    provider = relationship('Provider')

    user_id = sql.Column(sql.Integer, sql.ForeignKey('user.id'))
    user = relationship('User', back_populates='accounts')

    playlists = relationship('Playlist', back_populates='account')

    title = sql.Column(sql.String(64))
    image_id = sql.Column(sql.Integer, sql.ForeignKey('image.id'))
    image = relationship('Image')

    created = sql.Column(
        sql.DateTime(timezone=True), server_default=func.now())
    updated = sql.Column(sql.DateTime(timezone=True), onupdate=func.now())

    access_token = sql.Column(sql.String(256))
    refresh_token = sql.Column(sql.String(256))
    token_expiration = sql.Column(sql.DateTime(timezone=True))

    @property
    def client_id(self):
        if self.provider_id == 'youtube':
            auth_class = cloudplayer.api.auth.Youtube
        elif self.provider_id == 'soundcloud':
            auth_class = cloudplayer.api.auth.Soundcloud
        else:
            return
        settings_key = auth_class._OAUTH_SETTINGS_KEY
        return opt.options[settings_key]['api_key']


class Image(Base):

    __tablename__ = 'image'
    __fields__ = ['id', 'small', 'medium', 'large']

    id = sql.Column(sql.Integer, primary_key=True)
    small = sql.Column(sql.String(256))
    medium = sql.Column(sql.String(256))
    large = sql.Column(sql.String(256))


class Playlist(Base):

    __tablename__ = 'playlist'
    __fields__ = ['id', 'account_id', 'provider_id',
                  'title', 'public', 'follower_count']
    __table_args__ = (
        sql.ForeignKeyConstraint(
            ['provider_id', 'account_id'],
            ['account.provider_id', 'account.id']),)

    id = sql.Column(sql.Integer, primary_key=True)

    account_id = sql.Column(sql.String(32))
    provider_id = sql.Column(sql.String(16))
    account = relationship('Account', back_populates='playlists')

    title = sql.Column(sql.String(512))
    public = sql.Column(sql.Boolean, default=False)
    follower_count = sql.Column(sql.Integer, default=0)

    playlist_items = relationship('PlaylistItem')


class PlaylistItem(Base):

    __tablename__ = 'PlaylistItem'
    __fields__ = ['rank', 'track']

    playlist_id = sql.Column(
        sql.Integer, sql.ForeignKey('playlist.id'), primary_key=True)
    track_id = sql.Column(
        sql.String(128), sql.ForeignKey('track.id'), primary_key = True)
    track = relationship('Track')

    rank = sql.Column(sql.Integer)


class Track(Base):

    __tablename__ = 'track'
    __fields__ = ['id', 'account_id', 'provider_id',
                  'title', 'play_count', 'like_count', 'aspect_ratio',
                  'created', 'duration', 'image']
    __table_args__ = (
        sql.ForeignKeyConstraint(
            ['provider_id', 'account_id'],
            ['account.provider_id', 'account.id']),)

    id = sql.Column(sql.String(128), primary_key=True)

    account_id = sql.Column(sql.String(32))
    provider_id = sql.Column(sql.String(16))
    account = relationship('Account')

    title = sql.Column(sql.String)

    play_count = sql.Column(sql.Integer)
    like_count = sql.Column(sql.Integer)
    aspect_ratio = sql.Column(sql.Float)
    created = sql.Column(sql.DateTime(timezone=True))
    duration = sql.Column(sql.Interval)

    image_id = sql.Column(sql.Integer, sql.ForeignKey('image.id'))
    image = relationship('Image')


class Provider(Base):

    __tablename__ = 'provider'
    __fields__ = ['id']

    id = sql.Column(sql.String(12), primary_key=True)


class User(Base):

    __tablename__ = 'user'
    __fields__ = ['id', 'accounts', 'created', 'updated']

    id = sql.Column(sql.Integer, primary_key=True)

    accounts = relationship('Account', back_populates='user')

    created = sql.Column(
        sql.DateTime(timezone=True), server_default=func.now())
    updated = sql.Column(sql.DateTime(timezone=True), onupdate=func.now())
