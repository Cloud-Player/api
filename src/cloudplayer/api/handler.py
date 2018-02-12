"""
    cloudplayer.api.handler
    ~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import redis
import tornado.auth
import tornado.escape
import tornado.gen
import tornado.httputil
import tornado.options as opt
import tornado.web

from cloudplayer.api.model import Encoder
from cloudplayer.api.controller.auth import create_controller
from cloudplayer.api.model.account import Account
from cloudplayer.api.policy import PolicyViolation
from cloudplayer.api.model.user import User


class HandlerMixin(object):

    @property
    def cache(self):
        if not hasattr(self, '_cache'):
            self._cache = redis.Redis(
                connection_pool=self.application.redis_pool)
        return self._cache

    @property
    def http_client(self):
        if not hasattr(self, '_http_client'):
            self._http_client = tornado.httpclient.AsyncHTTPClient()
        return self._http_client

    @property
    def db(self):
        if not hasattr(self, '_db'):
            self._db = self.application.database.create_session()
        return self._db

    def finish(self, *args, **kw):
        self.db.close()
        super().finish(*args, **kw)

    def write_error(self, status_code, **kw):
        reason = 'no reason given'
        if 'reason' in kw:
            reason = kw['reason']
        elif 'exc_info' in kw:
            exception = kw['exc_info'][1]
            for attr in ('reason', 'message', 'log_message'):
                if getattr(exception, attr, None):
                    reason = getattr(exception, attr)
                    break
        self.set_status(status_code)
        self.write({'status_code': status_code, 'reason': reason})

    @tornado.gen.coroutine
    def fetch(self, provider_id, path, **kw):
        controller = create_controller(
            provider_id, self.db, self.current_user)
        response = yield controller.fetch(path, **kw)
        return response


class ControllerHandlerMixin(object):

    __controller__ = NotImplemented

    @property
    def controller(self):
        if not hasattr(self, '_controller'):
            self._controller = self.__controller__(self.db, self.current_user)
        return self._controller


class EntityMixin(ControllerHandlerMixin):

    SUPPORTED_METHODS = ('GET', 'PATCH', 'DELETE')

    @tornado.gen.coroutine
    def get(self, **ids):
        try:
            entity = yield self.controller.read(ids)
        except PolicyViolation as violation:
            self.write_error(403, reason=violation.message)
        else:
            yield self.write(entity)

    @tornado.gen.coroutine
    def patch(self, **ids):
        try:
            entity = yield self.controller.update(ids, **self.body)
        except PolicyViolation as violation:
            self.write_error(403, reason=violation.message)
        else:
            yield self.write(entity)

    @tornado.gen.coroutine
    def delete(self, **ids):
        try:
            entity = yield self.controller.delete(ids)
        except PolicyViolation as violation:
            self.write_error(403, reason=violation.message)
        else:
            self.set_status(204)
            self.finish()


class CollectionMixin(ControllerHandlerMixin):

    SUPPORTED_METHODS = ('GET', 'POST')

    @tornado.gen.coroutine
    def get(self, **ids):
        query = dict(self.query_params)
        try:
            entities = yield self.controller.search(ids, **query)
        except PolicyViolation as violation:
            self.write_error(403, reason=violation.message)
        else:
            yield self.write(entities)

    @tornado.gen.coroutine
    def post(self, **ids):
        try:
            entity = yield self.controller.create(ids, **self.body)
        except PolicyViolation as violation:
            self.write_error(403, reason=violation.message)
        else:
            yield self.write(entity)
