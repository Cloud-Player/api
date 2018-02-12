"""
    cloudplayer.api.model.image
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import sqlalchemy as sql

from cloudplayer.api.model import Base


class Image(Base):

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
