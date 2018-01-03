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
            provider, path, method=method, params=params)
        yield self.write_response(response)

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


class Youtube(Proxy):

    def write_response(self, data):
        tornado.web.RequestHandler.write(self, response.body)
        self.finish()


class Soundcloud(Proxy):

    @property
    def api_key(self):
        settings_key = cloudplayer.api.auth.Soundcloud._OAUTH_SETTINGS_KEY
        return self.settings[settings_key]['api_key']

    def write_response(self, response):
        def append_client_id(match):
            return '{}?{}'.format(match.group(0), self.api_key)

        data = re.sub(
            '(api\.soundcloud\.com/tracks/[0-9]+/stream)',
            append_client_id,
            response.body.decode('utf-8'))

        tornado.web.RequestHandler.write(self, data)
        self.finish()
