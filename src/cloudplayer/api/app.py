"""
    cloudplayer.api.app
    ~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import functools
import signal
import sys

import bugsnag
import redis
import sqlalchemy as sql
import sqlalchemy.orm as orm
import tornado.concurrent
import tornado.httpclient
import tornado.ioloop
import tornado.options as opt
import tornado.web
from sqlalchemy import event
from tornado.log import app_log

from cloudplayer.api.routing import ProtocolMatches


def define_options():  # pragma: no cover
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
    opt.define('youtube', type=dict, group='app')
    opt.define('soundcloud', type=dict, group='app')
    opt.define('bugsnag', type=dict, group='app')
    opt.define('cloudplayer', type=dict, group='app')
    opt.define('providers', type=list, group='app')
    opt.define('allowed_origins', type=list, group='app')
    opt.define('num_executors', type=int, default=1, group='app')
    opt.define('redirect_state', type=str, default='v3', group='app')
    opt.define('redis_host', type=str, default='127.0.0.1', group='app')
    opt.define('redis_port', type=int, default=6379, group='app')
    opt.define('redis_db', type=int, default=0, group='app')
    opt.define('redis_password', type=int, default=None, group='app')
    opt.define('postgres_host', type=str, default='127.0.0.1', group='app')
    opt.define('postgres_port', type=int, default=5432, group='app')
    opt.define('postgres_db', type=str, default='cloudplayer', group='app')
    opt.define('postgres_user', type=str, default='api', group='app')
    opt.define('postgres_password', type=str, default='password', group='app')
    opt.parse_config_file(opt.options.config)


class Application(tornado.web.Application):
    """Wraps routing configuration and data source connections."""

    http_routes = [
        (r'^/account/(?P<provider_id>[a-z]+)'
         r'/(?P<id>[0-9a-zA-Z]+)$',
         'cloudplayer.api.http.account.Entity'),

        (r'^/playlist/(?P<provider_id>[a-z]+)$',
         'cloudplayer.api.http.playlist.Collection'),
        (r'^/playlist/(?P<provider_id>[a-z]+)'
         r'/(?P<id>[0-9a-zA-Z]+)$',
         'cloudplayer.api.http.playlist.Entity'),

        ((r'^/playlist/(?P<playlist_provider_id>[a-z]+)'
          r'/(?P<playlist_id>[0-9a-zA-Z]+)'
          r'/item$'),
         'cloudplayer.api.http.playlist_item.Collection'),
        ((r'^/playlist/(?P<playlist_provider_id>[a-z]+)'
          r'/(?P<playlist_id>[0-9a-zA-Z]+)'
          r'/item'
          r'/(?P<id>[0-9]+)$'),
         'cloudplayer.api.http.playlist_item.Entity'),

        (r'^/favourite/(?P<provider_id>[a-z]+)'
         r'/(?P<id>[0-9a-zA-Z]+)$',
         'cloudplayer.api.http.favourite.Entity'),

        ((r'^/favourite/(?P<favourite_provider_id>[a-z]+)'
          r'/(?P<favourite_id>[0-9a-zA-Z]+)'
          r'/item$'),
         'cloudplayer.api.http.favourite_item.Collection'),
        ((r'^/favourite/(?P<favourite_provider_id>[a-z]+)'
          r'/(?P<favourite_id>[0-9a-zA-Z]+)'
          r'/item'
          r'/(?P<id>[0-9]+)$'),
         'cloudplayer.api.http.favourite_item.Entity'),

        (r'^/provider$',
         'cloudplayer.api.http.provider.Collection'),
        (r'^/provider/(?P<id>[a-z]+)$',
         'cloudplayer.api.http.provider.Entity'),

        (r'^/session$',
         'cloudplayer.api.http.session.Collection'),

        (r'^/token$',
         'cloudplayer.api.http.token.Collection'),
        (r'^/token/(?P<id>[0-9a-z]+)$',
         'cloudplayer.api.http.token.Entity'),

        (r'^/track/(?P<provider_id>soundcloud)'
         r'/(?P<id>[0-9a-zA-Z]+)$',
         'cloudplayer.api.http.track.Soundcloud'),
        (r'^/track/(?P<provider_id>youtube)'
         r'/(?P<id>[0-9a-zA-Z-_]+)$',
         'cloudplayer.api.http.track.Youtube'),

        (r'^/track/(?P<track_provider_id>soundcloud)'
         r'/(?P<track_id>[0-9a-zA-Z]+)'
         r'/comment$',
         'cloudplayer.api.http.track_comment.Soundcloud'),

        (r'^/user/(?P<id>me|[0-9]+)$',
         'cloudplayer.api.http.user.Entity'),

        (r'^/websocket$',
         'cloudplayer.api.http.socket.Handler'),

        (r'^/soundcloud$',
         'cloudplayer.api.http.auth.Soundcloud'),
        (r'^/youtube$',
         'cloudplayer.api.http.auth.Youtube'),

        (r'^/proxy/(soundcloud|youtube)/(.*)',
         'cloudplayer.api.http.proxy.Proxy'),

        (r'^/health_check$',
         'cloudplayer.api.http.base.HTTPHealth'),
        (r'^/.*',
         'cloudplayer.api.http.base.HTTPFallback'),
    ]

    ws_routes = [
        (r'^account\.(?P<provider_id>[a-z]+)'
         r'\.(?P<id>[0-9a-zA-Z]+)$',
         'cloudplayer.api.ws.account.Entity'),

        (r'^playlist\.(?P<provider_id>[a-z]+)'
         r'\.(?P<id>[0-9a-zA-Z]+)$',
         'cloudplayer.api.ws.playlist.Entity'),

        (r'^user\.(?P<id>me|[0-9]+)$',
         'cloudplayer.api.ws.user.Entity'),

        (r'^.*$',
         'cloudplayer.api.ws.base.WSFallback'),
    ]

    def __init__(self):
        settings = opt.options.group_dict('app')
        routes = [
            (ProtocolMatches('^http[s]?$'), list(self.http_routes)),
            (ProtocolMatches('^ws[s]?$'), list(self.ws_routes))
        ]
        super(Application, self).__init__(routes, **settings)

        if settings.get('bugsnag'):  # pragma: no cover
            bugsnag.configure(
                api_key=settings['bugsnag']['api_key'],
                project_root=settings['bugsnag']['project_root'])

        self.executor = tornado.concurrent.futures.ThreadPoolExecutor(
            settings['num_executors'])

        self.redis_pool = RedisPool.create(
            settings['redis_host'],
            settings['redis_port'],
            settings['redis_db'],
            settings['redis_password'])

        self.database = Database(
            settings['postgres_user'],
            settings['postgres_password'],
            settings['postgres_host'],
            settings['postgres_port'],
            settings['postgres_db'])

        self.event_mapper = EventMapper(
            self.database,
            self.redis_pool)

    def shutdown(self):
        self.event_mapper.shutdown()
        self.database.shutdown()
        RedisPool.disconnect(self.redis_pool)


class RedisPool(object):

    @staticmethod
    def create(host, port, db, password):
        redis_pool = redis.ConnectionPool(
            host=host, port=port, db=db, password=password)
        app_log.info('connecting to {host}:{port}/{db}'.format(
            **redis_pool.connection_kwargs))
        return redis_pool

    @staticmethod
    def disconnect(redis_pool):
        app_log.info('shutting down {host}:{port}/{db}'.format(
            **redis_pool.connection_kwargs))
        redis_pool.disconnect()


class Database(object):
    """Postgres database session factory that insures initialization."""

    def __init__(self, user, password, host, port, db):
        self.address = '{}:{}/{}'.format(host, port, db)
        uri = 'postgresql://{}:{}@{}'.format(user, password, self.address)
        self.engine = sql.create_engine(uri, client_encoding='utf8')
        self.session_cls = orm.sessionmaker(bind=self.engine)
        self.initialize()

    def initialize(self):
        app_log.info('connecting to {}'.format(self.address))
        self.ensure_tables()
        self.populate_providers()

    def ensure_tables(self):
        from cloudplayer.api.model.base import Base
        Base.metadata.create_all(self.engine)

    def populate_providers(self):
        from cloudplayer.api.model.provider import Provider
        session = self.create_session()
        for provider_id in opt.options.providers:
            if not session.query(Provider).get(provider_id):
                entity = Provider(id=provider_id)
                session.add(entity)
        session.commit()
        session.close()

    def create_session(self):
        return self.session_cls()

    def shutdown(self):
        app_log.info('shutting down {}'.format(self.address))
        self.engine.pool.dispose()


class EventMapper(object):

    def __init__(self, database, redis_pool):
        self.database = database
        self.redis_pool = redis_pool
        self.listeners = []
        self.hook_map = {
            'after_insert': 'post',
            'after_update': 'put',
            'after_delete': 'delete'}
        self.initialize()

    def initialize(self):
        from cloudplayer.api.model.base import Base
        for model in Base._decl_class_registry.values():
            if not getattr(model, '__channel__', None):
                continue
            for hook, method in self.hook_map.items():
                func = functools.partial(
                    model.event_hook,
                    self.redis_pool,
                    method)
                event.listen(model, hook, func)
                self.listeners.append((model, hook, func))

        app_log.info('registered {} listeners'.format(len(self.listeners)))

    def shutdown(self):
        app_log.info('removing {} listeners'.format(len(self.listeners)))
        for listener in self.listeners:
            event.remove(*listener)


def configure_httpclient():
    """Try to configure an async httpclient"""
    defaults = opt.options.group_dict('httpclient')
    try:
        tornado.httpclient.AsyncHTTPClient.configure(
            'tornado.curl_httpclient.CurlAsyncHTTPClient', defaults=defaults)
    except ImportError:  # pragma: no cover
        app_log.warn('could not setup curl client, using simple http instead')
        tornado.httpclient.AsyncHTTPClient.configure(None, defaults=defaults)


def main():  # pragma: no cover
    """Main tornado application entry point"""
    define_options()
    configure_httpclient()
    app = Application()
    app.listen(opt.options.port)
    app_log.info('server listening at 127.0.0.1:%s', opt.options.port)
    ioloop = tornado.ioloop.IOLoop.current()

    def shutdown(*args):
        """Signal handler callback that shuts down the ioloop"""
        app_log.info('server shutting down')
        app.shutdown()
        ioloop.stop()
        app_log.info('exit')
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)

    try:
        ioloop.start()
    except KeyboardInterrupt:
        shutdown()


if __name__ == '__main__':  # pragma: no cover
    main()
