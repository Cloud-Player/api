"""
    cloudplayer.api.model.tracklist_item
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
from sqlalchemy.ext.declarative import declared_attr
import sqlalchemy as sql
import sqlalchemy.orm as orm


class TracklistItemMixin(object):

    id = sql.Column(sql.Integer)

    account_provider_id = sql.Column(sql.String(16), nullable=False)
    account_id = sql.Column(sql.String(32), nullable=False)

    @declared_attr
    def provider_id(cls):
        return orm.synonym('track_provider_id')

    @declared_attr
    def account(cls):
        return orm.relationship('Account')

    track_provider_id = sql.Column(sql.String(16), nullable=False)
    track_id = sql.Column(sql.String(128), nullable=False)
