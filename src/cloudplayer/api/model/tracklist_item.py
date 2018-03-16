"""
    cloudplayer.api.model.tracklist_item
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import sqlalchemy as sql
import sqlalchemy.orm as orm
from sqlalchemy.ext.declarative import declared_attr


class TracklistItemMixin(object):

    id = sql.Column(sql.Integer)

    account_provider_id = sql.Column(sql.String(16), nullable=False)
    account_id = sql.Column(sql.String(32), nullable=False)

    @declared_attr
    def account(cls):
        return orm.relation(
            'Account',
            single_parent=True)

    track_provider_id = sql.Column(sql.String(16), nullable=False)
    track_id = sql.Column(sql.String(128), nullable=False)
