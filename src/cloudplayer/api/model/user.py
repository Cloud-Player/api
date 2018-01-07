"""
    cloudplayer.api.model.user
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
from sqlalchemy.sql import func
import sqlalchemy as sql
import sqlalchemy.orm as orm

from cloudplayer.api.model import Base


class User(Base):

    __tablename__ = 'user'
    __fields__ = [
        'id',
        'accounts',
        'created',
        'updated'
    ]
    __filters__ = []
    __mutable__ = []
    __public__ = [
        'id',
        'accounts'
    ]
    __table_args__ = (
        sql.PrimaryKeyConstraint(
            'id'),
    )

    id = sql.Column(sql.Integer)

    accounts = orm.relationship('Account', back_populates='user')

    created = sql.Column(
        sql.DateTime(timezone=True), server_default=func.now())
    updated = sql.Column(
        sql.DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now())
