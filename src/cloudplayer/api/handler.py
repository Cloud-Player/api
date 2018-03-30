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
import tornado.web
from tornado.log import app_log, gen_log

from cloudplayer.api import APIException


class HandlerMixin(object):

    @property
    def cache(self):
        if not hasattr(self, '_cache'):
            self._cache = redis.Redis(
                connection_pool=self.application.redis_pool)
        return self._cache

    @property
    def pubsub(self):
        if not hasattr(self, '_pubsub'):
            self._pubsub = self.cache.pubsub()
            self._pubsub.subscribe(keep_alive=lambda _: True)
        return self._pubsub

    @pubsub.setter
    def pubsub(self, value):
        self._pubsub = value
        self._pubsub.subscribe(keep_alive=lambda _: True)

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

    def on_finish(self):
        if hasattr(self, '_db'):
            self._db.close()

    def write_error(self, status_code, **kw):
        self.write({'status_code': status_code, 'reason': self._reason})

    def _request_summary(self):
        return '%s %s %s (%s)' % (
            self.request.protocol.upper(),
            self.request.method.upper(),
            self.request.uri,
            self.request.remote_ip)

    def log_exception(self, type_, value, tb):
        if isinstance(value, APIException):
            if value.log_message:
                args = (value.status_code, self._request_summary(),
                        value.log_message % value.args)
                gen_log.warning('%d %s: %s', *args)
        else:
            app_log.error('uncaught exception %s', self._request_summary(),
                          exc_info=(type_, value, tb))


class ControllerHandlerMixin(object):

    __controller__ = NotImplemented

    @property
    def controller(self):
        if not hasattr(self, '_controller'):
            self._controller = self.__controller__(
                self.db, self.current_user, self.pubsub)
        return self._controller


class EntityMixin(ControllerHandlerMixin):

    SUPPORTED_METHODS = ('GET', 'PUT', 'PATCH', 'DELETE', 'SUB', 'UNSUB')

    @tornado.gen.coroutine
    def get(self, **ids):
        entity = yield self.controller.read(ids)
        yield self.write(entity)

    @tornado.gen.coroutine
    def put(self, **ids):
        entity = yield self.controller.update(ids, self.body)
        yield self.write(entity)

    @tornado.gen.coroutine
    def patch(self, **ids):
        entity = yield self.controller.update(ids, self.body)
        yield self.write(entity)

    @tornado.gen.coroutine
    def delete(self, **ids):
        yield self.controller.delete(ids)
        self.set_status(204)
        self.finish()

    @tornado.gen.coroutine
    def sub(self, **ids):
        yield self.controller.sub(ids, {self.request.channel: self.forward})
        self.set_status(204)
        self.finish()

    @tornado.gen.coroutine
    def unsub(self, **ids):
        yield self.controller.unsub(ids, {self.request.channel: None})
        self.set_status(204)
        self.finish()


class CollectionMixin(ControllerHandlerMixin):

    SUPPORTED_METHODS = ('GET', 'POST')

    @tornado.gen.coroutine
    def get(self, **ids):
        query = dict(self.query_params)
        entities = yield self.controller.search(ids, query)
        yield self.write(entities)

    @tornado.gen.coroutine
    def post(self, **ids):
        entity = yield self.controller.create(ids, self.body)
        yield self.write(entity)
