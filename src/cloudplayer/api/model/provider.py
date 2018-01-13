"""
    cloudplayer.api.model.provider
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
import sqlalchemy as sql
import sqlalchemy.orm as orm
import tornado.options as opt

from cloudplayer.api.model import Base
import cloudplayer.api.http.auth


class Provider(Base):

    __fields__ = [
        'id',
        'client_id'
    ]
    __filters__ = []
    __mutable__ = []
    __public__ = __fields__
    __table_args__ = (
        sql.PrimaryKeyConstraint(
            'id'),
    )

    id = sql.Column(sql.String(12))

    provider_id = orm.synonym('id')

    @property
    def client_id(self):
        if self.id == 'youtube':
            auth_class = cloudplayer.api.handler.auth.Youtube
        elif self.id == 'soundcloud':
            auth_class = cloudplayer.api.handler.auth.Soundcloud
        else:
            return
        settings_key = auth_class._OAUTH_SETTINGS_KEY
        return opt.options[settings_key]['api_key']
