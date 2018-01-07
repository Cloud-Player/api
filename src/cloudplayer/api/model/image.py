"""
    cloudplayer.api.model.image
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
from sqlalchemy.sql import func
import sqlalchemy as sql

from cloudplayer.api.model import Base


class Image(Base):

    __tablename__ = 'image'
    __fields__ = [
        'id',
        'small',
        'medium',
        'large'
    ]
    __filters__ = []
    __mutable__ = [
        'small',
        'medium',
        'large'
    ]
    __public__ = __fields__
    __table_args__ = (
        sql.PrimaryKeyConstraint(
            'id'),
    )

    id = sql.Column(sql.Integer)
    small = sql.Column(sql.String(256))
    medium = sql.Column(sql.String(256))
    large = sql.Column(sql.String(256), nullable=False)

    created = sql.Column(
        sql.DateTime(timezone=True), server_default=func.now())
    updated = sql.Column(
        sql.DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now())
