"""
    cloudplayer.api.app
    ~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: Apache-2.0, see LICENSE for details
"""
import signal
import sys

from tornado.log import app_log
import tornado.httpclient
import tornado.ioloop
import tornado.options as opt
import tornado.web

from cloudplayer.api import handler


def define_options():
    """Defines global configuration options"""
    opt.define('config', type=str, default='config.py')
    opt.define('port', type=int, default=8040)
    opt.parse_command_line()
    opt.define('connect_timeout', type=int, default=1, group='httpclient')
    opt.define('request_timeout', type=int, default=3, group='httpclient')
    opt.define('max_redirects', type=int, default=1, group='httpclient')
    opt.define('debug', type=bool, group='server')
    opt.define('xheaders', type=bool, group='server')
    opt.define('static_path', type=str, group='server')
    opt.define('allowed_origins', type=str, default='*')
    opt.parse_config_file(opt.options.config)


def make_app():
    """Configure routes and application options"""
    return tornado.web.Application([
        (r'^/.*', handler.FallbackHandler),
    ], **opt.options.group_dict('server'))


def configure_httpclient():
    """Try to configure an async httpclient"""
    defaults = opt.options.group_dict('httpclient')
    try:
        tornado.httpclient.AsyncHTTPClient.configure(
            'tornado.curl_httpclient.CurlAsyncHTTPClient', defaults=defaults)
    except ImportError:
        app_log.warn('could not setup curl client, using simple http instead')
        tornado.httpclient.AsyncHTTPClient.configure(None, defaults=defaults)


def main():
    """Main tornado application entry point"""
    define_options()
    configure_httpclient()
    app = make_app()
    app.listen(opt.options.port)
    app_log.info('server listening at localhost:%s', opt.options.port)
    ioloop = tornado.ioloop.IOLoop.current()

    def shutdown(*_):
        """Signal handler callback that shuts down the ioloop"""
        app_log.info('server shutting down')
        ioloop.stop()
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)

    try:
        ioloop.start()
    except KeyboardInterrupt:
        shutdown()


if __name__ == '__main__':
    main()
