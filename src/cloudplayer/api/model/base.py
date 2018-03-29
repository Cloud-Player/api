"""
    cloudplayer.api.base.model
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import datetime
import json
import time

import redis
import redis.exceptions
import sqlalchemy as sql
import sqlalchemy.inspection
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy.sql import expression
from sqlalchemy.types import DateTime
from tornado.log import app_log

from cloudplayer.api.access import Deny, Fields


class utcnow(expression.FunctionElement):
    type = DateTime()


@compiles(utcnow, 'postgresql')
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


class Transient(object):

    __acl__ = (Deny(),)
    __channel__ = ()
    __fields__ = ()

    def __init__(self, **kw):
        for field, value in kw.items():
            if hasattr(self, field):
                setattr(self, field, value)

    id = None
    account_id = None
    provider_id = 'cloudplayer'
    account_provider_id = property(lambda self: self.provider_id)
    parent = None
    created = None
    updated = None

    def _inspect_field(self, field):
        attr = getattr(self, field)
        is_list = isinstance(attr, list)
        if not is_list:
            attr = [attr]
        should_expand = all(isinstance(a, Transient) for a in attr)
        return should_expand, is_list

    @property
    def fields(self):
        return getattr(self, '_fields', Fields())

    @fields.setter
    def fields(self, value):
        """Fields can be a set of column names and include dotted syntax.

        A dotted field notation like `foo.bar` instructs the model to look up
        its `foo` relation and render its `bar` attribute.

            {'foo': {'bar': 42}}

        If the `foo` relation is one to many, the `bar` attribute is rendered
        from all the members in `foo`.

            {'foo': [{'bar': 73}, {'bar': 89}]}
        """
        tree = {}
        flat = []
        for field in value:
            key, *path = field.split('.', 1)
            flat.append(key)
            if path:
                tree[key] = tree.get(key, []) + list(path)
        for field, paths in tree.items():
            should_expand, is_list = self._inspect_field(field)
            if should_expand:
                relations = getattr(self, field)
                if not is_list:
                    relations = [relations]
                for relation in relations:
                    if isinstance(relation, Base):
                        relation.fields = Fields(*paths)
        self._fields = Fields(*flat)

    @property
    def account(self):
        # XXX: Check session for this account id without querying
        from cloudplayer.api.model.account import Account
        if self.account_id and self.provider_id:
            return Account(id=self.account_id, provider_id=self.provider_id)

    @classmethod
    def requires_account(cls):
        return False


class Model(Transient):
    """Abstract model class serving as the sqlalchemy declarative base.

    Defines sensible default values for commonly used attributes
    such as timestamps, ownership, acl and nested field expansion.
    """

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    created = sql.Column(
        sql.DateTime, server_default=utcnow())
    updated = sql.Column(
        sql.DateTime, server_default=utcnow(), onupdate=utcnow())

    def _inspect_field(self, field):
        prop = getattr(type(self), field).property
        should_expand = isinstance(prop, RelationshipProperty)
        is_list = prop.uselist
        return should_expand, is_list

    @property
    def account(self):
        # TODO: Check session for this account id without querying
        from cloudplayer.api.model.account import Account
        if self.account_id and self.provider_id:
            return Account(id=self.account_id, provider_id=self.provider_id)

    @classmethod
    def requires_account(cls):
        mapper = sqlalchemy.inspection.inspect(cls)
        prop = mapper.relationships.get('account', None)
        if prop:
            return not all(c.nullable for c in prop.local_columns)
        return False

    @staticmethod
    def event_hook(redis_pool, method, mapper, connection, target):
        target.fields = Fields(*target.__fields__)
        cache = redis.Redis(connection_pool=redis_pool)
        for pattern in target.__channel__:
            channel = pattern.format(**target.__dict__)
            message = json.dumps({
                'channel': channel,
                'method': method,
                'body': target},
                cls=Encoder)

            start = time.time()
            try:
                cache.publish(channel, message)
            except redis.exceptions.ConnectionError:
                status_code = 503
                host = '::1'
            else:
                status_code = 200
                host = cache.connection_pool.connection_kwargs['host']

            pub_time = 1000.0 * (time.time() - start)
            app_log.info('{} REDIS {} {} ({}) {:.2f}ms'.format(
                status_code, method.upper(), channel, host, pub_time))


Base = declarative_base(cls=Model)


class Encoder(json.JSONEncoder):
    """Custom JSON encoder for rendering granted fields."""

    def default(self, obj):
        try:
            return json.JSONEncoder.default(self, obj)
        except:  # NOQA
            if isinstance(obj, Transient):
                dict_ = {f: getattr(obj, f) for f in obj.fields}
                if dict_.get('id'):  # TODO: There must be a better solution
                    dict_['id'] = str(dict_['id'])
                return dict_
            elif isinstance(obj, datetime.datetime):
                return obj.isoformat()
            elif isinstance(obj, datetime.timedelta):
                return obj.total_seconds()
            return json.JSONEncoder.default(self, obj)
