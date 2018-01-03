"""
    cloudplayer.api.proxy
    ~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
import json
import re

import tornado.gen
import tornado.web

import cloudplayer.api.auth
import cloudplayer.api.handler


class Proxy(cloudplayer.api.handler.HTTPHandler):

    @tornado.gen.coroutine
    def proxy(self, method, provider, path):
        params = []
        for name, vals in self.request.query_arguments.items():
            for v in vals:
                params.append((name, v))

        response = yield self.fetch(
            provider, path, method=method, params=params,
            raise_error=False)
        if response.error:
            self.set_status(response.error.code)
        yield self.write_str(response.body)

    def write_str(self, data):
        tornado.web.RequestHandler.write(self, data)
        self.finish()

    @tornado.gen.coroutine
    def get(self, provider, path):
        yield self.proxy('GET', provider, path)

    @tornado.gen.coroutine
    def post(self, provider, path):
        yield self.proxy('POST', provider, path)

    @tornado.gen.coroutine
    def put(self, provider, path):
        yield self.proxy('PUT', provider, path)

    @tornado.gen.coroutine
    def delete(self, provider, path):
        yield self.proxy('DELETE', provider, path)
