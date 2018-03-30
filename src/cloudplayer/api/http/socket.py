"""
    cloudplayer.api.http.socket
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import json

import tornado.gen
import tornado.ioloop
from tornado.websocket import WebSocketHandler

from cloudplayer.api.http import HTTPHandler
from cloudplayer.api.ws import WSRequest


class Handler(HTTPHandler, WebSocketHandler):

    def __init__(self, application, request):
        WebSocketHandler.__init__(self, application, request)
        HTTPHandler.__init__(self, application, request)

    def open(self):
        self.listener = tornado.ioloop.PeriodicCallback(self.listen, 100)
        self.listener.start()

    @tornado.gen.coroutine
    def on_message(self, message):
        try:
            message = json.loads(message)
            assert isinstance(message, dict)
        except (AssertionError, ValueError):
            self.close(code=1003, reason='invalid json')
            return
        request = WSRequest(
            self.ws_connection,
            self.current_user,
            self.request,
            message)
        delegate = self.application.find_handler(request)
        handler = delegate.request_callback(self.application, request)
        try:
            yield handler()
        except Exception as exception:
            handler._handle_request_exception(exception)
        else:
            self.application.log_request(handler)
        finally:
            request.finish()
            handler.on_finish()

    def listen(self):
        if self.pubsub.subscribed:
            self.pubsub.get_message(ignore_subscribe_messages=True)
        else:
            self.pubsub.close()
            if self.listener.is_running():
                self.listener.stop()

    def on_close(self):
        if self.pubsub:
            self.pubsub.unsubscribe()

    def check_origin(self, origin):
        return origin in self.settings['allowed_origins']
