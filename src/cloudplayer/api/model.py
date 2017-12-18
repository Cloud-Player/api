"""
    cloudplayer.api.model
    ~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
import pkg_resources

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import sqlalchemy as sql
import sqlalchemy.ext.declarative


Base = sqlalchemy.ext.declarative.declarative_base()


class Account(Base):

    __tablename__ = 'account'

    id = sql.Column(sql.String(32), primary_key=True)

    provider_id = sql.Column(
        sql.String(16), sql.ForeignKey('provider.id'), primary_key=True)
    provider = relationship('Provider')

    user_id = sql.Column(sql.Integer, sql.ForeignKey('user.id'))
    user = relationship('User', back_populates='accounts')

    title = sql.Column(sql.String(64))
    image = sql.Column(sql.String(256))

    created = sql.Column(
        sql.DateTime(timezone=True), server_default=func.now())
    updated = sql.Column(sql.DateTime(timezone=True), onupdate=func.now())

    access_token = sql.Column(sql.String(256))
    refresh_token = sql.Column(sql.String(256))
    token_expiration = sql.Column(sql.DateTime(timezone=True))


class Provider(Base):

    __tablename__ = 'provider'

    id = sql.Column(sql.String(12), primary_key=True)


class User(Base):

    __tablename__ = 'user'

    id = sql.Column(sql.Integer, primary_key=True)

    accounts = relationship('Account', back_populates='user')

    created = sql.Column(
        sql.DateTime(timezone=True), server_default=func.now())
    updated = sql.Column(sql.DateTime(timezone=True), onupdate=func.now())
