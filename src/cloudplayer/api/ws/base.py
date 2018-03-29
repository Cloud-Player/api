"""
    cloudplayer.api.ws.base
    ~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import json
import sys
import time

from tornado.log import app_log
from tornado.escape import _unicode
import tornado.concurrent
import tornado.gen
import tornado.websocket
import tornado.httputil
import tornado.routing

from cloudplayer.api import APIException
from cloudplayer.api.model import Encoder
from cloudplayer.api.handler import HandlerMixin


WS_CODES = {
    1000: 'Normal Closure',
    1001: 'Going Away',
    1002: 'Protocol Error',
    1003: 'Unsupported Data',
    1005: 'No Status Recvd',
    1006: 'Abnormal Closure',
    1007: 'Invalid frame payload data',
    1008: 'Policy Violation',
    1009: 'Message too big',
    1010: 'Missing Extension',
    1011: 'Internal Error',
    1012: 'Service Restart',
    1013: 'Try Again Later',
    1014: 'Bad Gateway',
    1015: 'TLS Handshake'
}


class WSException(APIException):

    def __init__(self, status_code=1011, log_message='internal server error'):
        super().__init__(status_code, log_message)


class WSRequest(object):

    def __init__(self, connection, current_user, http_request, instruction):
        self.protocol = 'ws'
        self.connection = connection
        self.current_user = current_user
        self.remote_ip = http_request.remote_ip
        self.body = instruction.get('body', {})
        self.method = instruction.get('method', 'GET')
        self.query = instruction.get('query', {})
        self.channel = self.path = instruction.get('channel', 'null')
        self.sequence = instruction.get('sequence', 0)
        self._start_time = time.time()
        self._finish_time = None

    @property
    def uri(self):
        return self.channel

    def finish(self):
        self._finish_time = time.time()

    def request_time(self):
        if self._finish_time is None:
            return time.time() - self._start_time
        else:
            return self._finish_time - self._start_time


class WSBase(object):

    SUPPORTED_METHODS = ('GET', 'PATCH', 'POST', 'DELETE')

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
            raise WSException(405, 'method not allowed')

        method = getattr(self, self.request.method.lower())
        result = yield method(*self.path_args, **self.path_kwargs)
        if result is not None:
            result = yield result

    def decode_argument(self, value, name=None):
        try:
            return _unicode(value)
        except UnicodeDecodeError:
            raise WSException(400, 'invalid unicode argument')

    def write(self, data):
        message = json.dumps(
            {'channel': self.request.channel,
             'sequence': self.request.sequence,
             'body': data},
            cls=Encoder)
        self.request.connection.write_message(message)
        self.on_finish()

    def forward(self, data):
        message = json.dumps({data['channel']: json.loads(data['data'])})
        self.request.connection.write_message(message)

    def finish(self):
        self.request.finish()

    def _handle_request_exception(self, exception):
        self.log_exception(*sys.exc_info())
        if isinstance(exception, APIException):
            self.send_error(exception.status_code, exc_info=sys.exc_info())
            if 1000 <= exception.status_code <= 1015:
                app_log.error('closing socket %s', self._reason)
                self.request.connection.close(
                    exception.status_code, self._reason)
                self.request.connection = None
        else:
            self.send_error(500, exc_info=sys.exc_info())

    def send_error(self, status_code=500, **kw):
        reason = kw.get('reason')
        if 'exc_info' in kw:
            exception = kw['exc_info'][1]
            if isinstance(exception, APIException) and exception.log_message:
                reason = exception.log_message
        self.set_status(status_code, reason=reason)
        self.write_error(status_code, **kw)

    def set_status(self, status_code, reason=None):
        self._status_code = status_code
        if reason:
            self._reason = reason
        elif status_code in tornado.httputil.responses:
            self._reason = tornado.httputil.responses[status_code]
        elif status_code in WS_CODES:
            self._reason = WS_CODES[status_code]
        else:
            self._reason = 'no reason given'

    def get_status(self):
        return self._status_code


class WSHandler(HandlerMixin, WSBase):
    pass


class WSFallback(WSHandler):

    @tornado.gen.coroutine
    def get(self, **kw):
        raise WSException(404, 'channel not found')
