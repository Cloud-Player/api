"""
    cloudplayer.api.http.socket
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
import json

from tornado.websocket import WebSocketHandler
import tornado.ioloop
import tornado.gen

from cloudplayer.api.http import HTTPHandler
from cloudplayer.api.ws import WSRequest


class Handler(HTTPHandler, WebSocketHandler):

    def __init__(self, application, request):
        WebSocketHandler.__init__(self, application, request)
        HTTPHandler.__init__(self, application, request)
        self.pubsub = self.cache.pubsub()
        self.pubsub.subscribe(active=lambda _: True)

    def open(self):
        self.listener = tornado.ioloop.PeriodicCallback(self.listen, 100)
        self.listener.start()

    @tornado.gen.coroutine
    def on_message(self, message):
        if len(message) > 2 << 15:
            self.close(1011, 'message too big')
        try:
            message = json.loads(message)
            assert isinstance(message, dict)
        except (AssertionError, ValueError):
            self.close(code=1003, reason='invalid json')
        request = WSRequest(
            self.ws_connection,
            self.current_user,
            message)
        delegate = self.application.find_handler(request)
        handler = delegate.request_callback(self.application, request)
        yield handler()
        handler.finish()

    def listen(self):
        if self.pubsub.subscribed:
            self.pubsub.get_message(ignore_subscribe_messages=True)
        else:
            self.pubsub.close()
            if self.listener.is_running():
                self.listener.stop()

    def forward(self, data):
        message = json.dumps(
            {'channel': data['channel'],
             'body': json.loads(data['data'])})
        self.ws_connection.write_message(message)

    def on_close(self):
        if self.pubsub:
            self.pubsub.unsubscribe()

    def check_origin(self, origin):
        return origin in self.settings['allowed_origins']
