"""
    cloudplayer.api.http.proxy
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import tornado.web

from cloudplayer.api.controller import Controller
from cloudplayer.api.http import HTTPHandler


class Proxy(HTTPHandler):  # pragma: no cover

    SUPPORTED_METHODS = ('GET', 'POST', 'PUT', 'DELETE', 'OPTIONS')

    async def proxy(self, method, provider, path, **kw):
        controller = Controller(self.db, self.current_user)
        response = await controller.fetch(
            provider, path, method=method, params=self.query_params,
            raise_error=False, **kw)
        body = response.body
        if response.error:
            code = response.error.code
            if code == 599:
                code = 503
            if not body:
                body = response.error.message
            self.set_status(code)
        else:
            body = body.replace(  # Get your TLS on, YouTube!
                b'http://s.ytimg.com', b'https://s.ytimg.com')
        self.write_str(body)

    def write_str(self, data):
        tornado.web.RequestHandler.write(self, data)
        self.finish()

    async def get(self, provider, path):
        await self.proxy('GET', provider, path)

    async def post(self, provider, path):
        await self.proxy(
            'POST', provider, path,
            body=self.request.body,
            headers={'Content-Type': 'application/json'})

    async def put(self, provider, path):
        await self.proxy(
            'PUT', provider, path,
            body=self.request.body,
            headers={'Content-Type': 'application/json'})

    async def delete(self, provider, path):
        await self.proxy('DELETE', provider, path)
