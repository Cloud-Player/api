"""
    cloudplayer.api.model.image
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import sqlalchemy as sql

from cloudplayer.api.access import Allow, Deny, Everyone, Fields, Read
from cloudplayer.api.model import Base


class Image(Base):

    __acl__ = (
        Allow(Everyone, Read, Fields(
            'id',
            'small',
            'medium',
            'large',
            'created',
            'updated'
        )),
        Deny()
    )
    __table_args__ = (
        sql.PrimaryKeyConstraint(
            'id'),
    )

    id = sql.Column(sql.Integer)
    small = sql.Column(sql.String(256))
    medium = sql.Column(sql.String(256))
    large = sql.Column(sql.String(256), nullable=False)

    def copy(self):
        return Image(
            small=self.small,
            medium=self.medium,
            large=self.large)
