"""
    cloudplayer.api.ws.base
    ~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import json
import sys

from tornado.log import app_log
from tornado.escape import _unicode
import tornado.concurrent
import tornado.gen
import tornado.websocket
import tornado.httputil
import tornado.routing

from cloudplayer.api.model import Encoder
from cloudplayer.api.handler import HandlerMixin


class WSRequest(object):

    def __init__(self, connection, current_user, instruction):
        self.protocol = 'ws'
        self.connection = connection
        self.current_user = current_user
        self.body = instruction.get('body', {})
        self.method = instruction.get('method', 'GET')
        self.query = instruction.get('query', {})
        self.channel = self.path = instruction.get('channel', '')
        self.sequence = instruction.get('sequence', 0)


class WSBase(object):

    SUPPORTED_METHODS = ('GET', 'PATCH', 'POST', 'DELETE',
                         'SUBSCRIBE', 'UNSUBSCRIBE')

    def __init__(self, application, request, path_args=[], path_kwargs={}):
        self.application = application
        self.request = request
        self.path_args = [self.decode_argument(arg) for arg in path_args]
        self.path_kwargs = dict((k, self.decode_argument(v, name=k))
                                for (k, v) in path_kwargs.items())
        self.current_user = request.current_user
        self.body = request.body
        self.query_params = request.query
        self._status_code = 200
        self._reason = None

    @tornado.gen.coroutine
    def __call__(self):
        if self.request.method.upper() not in self.SUPPORTED_METHODS:
            self.write_error(405, 'method not allowed')
        else:
            method = getattr(self, self.request.method.lower())
            yield method(*self.path_args, **self.path_kwargs)

    def decode_argument(self, value, name=None):
        try:
            return _unicode(value)
        except UnicodeDecodeError:
            self.write_error(400, reason='invalid unicode')

    def write(self, data):
        message = json.dumps(
            {'channel': self.request.channel,
             'sequence': self.request.sequence,
             'body': data},
            cls=Encoder)
        self.request.connection.write_message(message)

    def write_error(self, status_code, **kw):
        if status_code < 999:
            super().write_error(status_code, **kw)
        elif self.request.connection:
            app_log.error('socket closed %s', self._reason)
            self.request.connection.close(status_code, self._reason)
            self.request.connection = None

    def set_status(self, status_code, reason=None):
        self._status_code = status_code
        if reason:
            self._reason = reason
        else:
            try:
                self._reason = tornado.httputil.responses[status_code]
            except KeyError:
                self._reason = 'no reason given'


class WSHandler(HandlerMixin, WSBase):
    pass


class WSFallback(WSHandler):

    @tornado.gen.coroutine
    def get(self, **kw):
        self.write_error(404, reason='resource not found')
