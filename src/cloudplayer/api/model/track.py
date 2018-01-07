"""
    cloudplayer.api.model.track
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
import datetime

import sqlalchemy as sql
import sqlalchemy.orm as orm

from cloudplayer.api.model import Base


class Track(Base):

    __tablename__ = 'track'
    __fields__ = [
        'id',
        'account_id',
        'provider_id',
        'title',
        'play_count',
        'like_count',
        'aspect_ratio',
        'created',
        'duration',
        'image'
    ]
    __filters__ = []
    __mutable__ = []
    __public__ = __fields__
    __table_args__ = (
        sql.PrimaryKeyConstraint(
            'id', 'provider_id'),
        sql.ForeignKeyConstraint(
            ['provider_id'],
            ['provider.id']),
        sql.ForeignKeyConstraint(
            ['account_id', 'provider_id'],
            ['account.id', 'account.provider_id']),
        sql.ForeignKeyConstraint(
            ['image_id'],
            ['image.id']),
    )

    id = sql.Column(sql.String(96))

    provider_id = sql.Column(sql.String(16))
    provider = orm.relationship('Provider')

    account_id = sql.Column(sql.String(32), nullable=False)
    account = orm.relationship(
        'Account', back_populates='tracks', viewonly=True)

    title = sql.Column(sql.String, nullable=False)

    play_count = sql.Column(sql.Integer, default=0)
    like_count = sql.Column(sql.Integer, default=0)
    aspect_ratio = sql.Column(sql.Float, default=1.0)
    created = sql.Column(sql.DateTime(timezone=True))
    duration = sql.Column(sql.Interval, default=datetime.timedelta())

    image_id = sql.Column(sql.Integer, nullable=False)
    image = orm.relationship('Image')
