"""
    cloudplayer.api.app
    ~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
import signal
import sys

from tornado.log import app_log
import redis
import sqlalchemy as sql
import sqlalchemy.orm
import tornado.concurrent
import tornado.httpclient
import tornado.ioloop
import tornado.options as opt
import tornado.web

from cloudplayer.api import auth
from cloudplayer.api import handler
from cloudplayer.api import model
from cloudplayer.api import playlist
from cloudplayer.api import user


def define_options():
    """Defines global configuration options"""
    opt.define('config', type=str, default='dev.py')
    opt.define('port', type=int, default=8040)
    opt.parse_command_line()
    opt.define('connect_timeout', type=int, default=1, group='httpclient')
    opt.define('request_timeout', type=int, default=3, group='httpclient')
    opt.define('max_redirects', type=int, default=1, group='httpclient')
    opt.define('debug', type=bool, group='app')
    opt.define('xheaders', type=bool, group='app')
    opt.define('static_path', type=str, group='app')
    opt.define('jwt_cookie', default='tok_v1', group='app')
    opt.define('jwt_expiration', default=30, group='app')
    opt.define('jwt_secret', type=str, group='app')
    opt.define('youtube_oauth', type=dict, group='app')
    opt.define('soundcloud_oauth', type=dict, group='app')
    opt.define('providers', type=list, group='app')
    opt.define('allowed_origins', type=list, group='app')
    opt.define('num_executors', type=int, default=1, group='app')
    opt.define('redis_host', type=str, default='localhost', group='app')
    opt.define('redis_port', type=int, default=6379, group='app')
    opt.define('postgres_host', type=str, default='localhost', group='app')
    opt.define('postgres_port', type=int, default=5432, group='app')
    opt.define('postgres_db', type=str, default='cloudplayer', group='app')
    opt.define('postgres_user', type=str, default='api', group='app')
    opt.define('postgres_password', type=str, default='password', group='app')
    opt.parse_config_file(opt.options.config)


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r'^/youtube$', auth.Youtube),
            (r'^/playlist$', playlist.Collection),
            (r'^/soundcloud$', auth.Soundcloud),
            (r'^/user/(me|[0-9]+)$', user.Entity),
            (r'^/.*', handler.FallbackHandler)
        ]
        settings = opt.options.group_dict('app')

        super(Application, self).__init__(handlers, **settings)

        self.executor = tornado.concurrent.futures.ThreadPoolExecutor(
            settings['num_executors'])

        self.redis_pool = redis.ConnectionPool(
            host=settings['redis_host'],
            port=settings['redis_port'])

        self.database = Database(
            settings['postgres_user'],
            settings['postgres_password'],
            settings['postgres_host'],
            settings['postgres_port'],
            settings['postgres_db'])


class Database(object):

    def __init__(self, user, password, host, port, db):
        url = 'postgresql://{}:{}@{}:{}/{}'.format(
            user, password, host, port, db)
        self.engine = sql.create_engine(url, client_encoding='utf8')
        model.Base.metadata.create_all(self.engine)
        self.session_cls = sqlalchemy.orm.sessionmaker(bind=self.engine)
        self.populate_providers()

    def populate_providers(self):
        session = self.create_session()
        for provider_id in opt.options.providers:
            if not session.query(model.Provider).get(provider_id):
                provider = model.Provider(id=provider_id)
                session.add(provider)
        session.commit()

    def create_session(self):
        return self.session_cls()


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
    app = Application()
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
