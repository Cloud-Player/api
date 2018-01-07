"""
    cloudplayer.api.base.model
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""

import json
import datetime
import pkg_resources

import sqlalchemy as sql
import sqlalchemy.ext.declarative


class Model(object):

    __fields__ = []
    __filters__ = []
    __mutable__ = []
    __public__ = []

    account_id = None
    provider_id = None


Base = sqlalchemy.ext.declarative.declarative_base(cls=Model)


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
