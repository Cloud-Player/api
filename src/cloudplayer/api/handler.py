"""
    cloudplayer.api.handler
    ~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: Apache-2.0, see LICENSE for details
"""
import json

import tornado.options as opt
import tornado.web


class HTTPHandler(tornado.web.RequestHandler):

    SUPPORTED_METHODS = ('GET', 'POST', 'DELETE', 'PUT', 'OPTIONS')

    def set_default_headers(self):
        headers = [
            ('Access-Control-Allow-Credentials', 'true'),
            ('Access-Control-Allow-Headers', 'Accept, Content-Type, Origin'),
            ('Access-Control-Allow-Methods', self.allowed_methods),
            ('Access-Control-Allow-Origin', self.allowed_origin),
            ('Access-Control-Max-Age', '600'),
            ('Cache-Control', 'no-cache, no-store, must-revalidate'),
            ('Content-Language', 'en-US'),
            ('Content-Type', 'application/json'),
            ('Pragma', 'no-cache'),
            ('Server', 'cloudplayer')
        ]
        for header, value in headers:
            self.set_header(header, value)

    def write(self, data):
        json.dump(data, super(HTTPHandler, self))
        self.finish()

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
        self.write({'status_code': status_code, 'reason': reason})

    @tornado.gen.coroutine
    def options(self, *args, **kwargs):
        self.finish()

    @property
    def allowed_origin(self):
        if not hasattr(HTTPHandler, '_allowed_origins'):
            HTTPHandler._allowed_origins = (
                opt.options.allowed_origins.replace(' ', '').split(','))
        proposed_origin = self.request.headers.get('Origin')
        if proposed_origin in self._allowed_origins:
            return proposed_origin
        return self._allowed_origins[0]

    @property
    def allowed_methods(self):
        return ', '.join(self.SUPPORTED_METHODS)


class FallbackHandler(HTTPHandler):

    def get(self, *args, **kwargs):
        self.send_error(404, reason='resource not found')
