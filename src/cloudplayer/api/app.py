"""
    cloudplayer.api.app
    ~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
import signal
import sys

from tornado.log import app_log
from tornado.routing import RuleRouter, Rule
import bugsnag
import redis
import sqlalchemy as sql
import sqlalchemy.orm as orm
import tornado.concurrent
import tornado.httpclient
import tornado.ioloop
import tornado.options as opt
import tornado.web

from cloudplayer.api.routing import ProtocolMatches


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
    opt.define('youtube', type=dict, group='app')
    opt.define('soundcloud', type=dict, group='app')
    opt.define('bugsnag', type=dict, group='app')
    opt.define('cloudplayer', type=dict, group='app')
    opt.define('providers', type=list, group='app')
    opt.define('allowed_origins', type=list, group='app')
    opt.define('num_executors', type=int, default=1, group='app')
    opt.define('menuflow_state', type=str, default='v3', group='app')
    opt.define('redis_host', type=str, default='localhost', group='app')
    opt.define('redis_port', type=int, default=6379, group='app')
    opt.define('redis_db', type=int, default=0, group='app')
    opt.define('redis_password', type=int, default=None, group='app')
    opt.define('postgres_host', type=str, default='localhost', group='app')
    opt.define('postgres_port', type=int, default=5432, group='app')
    opt.define('postgres_db', type=str, default='cloudplayer', group='app')
    opt.define('postgres_user', type=str, default='api', group='app')
    opt.define('postgres_password', type=str, default='password', group='app')
    opt.parse_config_file(opt.options.config)


class Application(tornado.web.Application):

    http_routes = [
        (r'^/soundcloud$',
         'cloudplayer.api.http.auth.Soundcloud'),
        (r'^/youtube$',
         'cloudplayer.api.http.auth.Youtube'),

        (r'^/token/(?P<id>[0-9a-z]+)$',
         'cloudplayer.api.http.token.Entity'),
        (r'^/token$',
         'cloudplayer.api.http.token.Collection'),

        (r'^/account/(?P<provider_id>[a-z]+)/(?P<id>[0-9a-zA-Z]+)$',
         'cloudplayer.api.http.account.Entity'),

        ((r'^/playlist/(?P<playlist_provider_id>[a-z]+)'
          r'/(?P<playlist_id>[0-9a-zA-Z]+)'
          r'/item/(?P<id>[0-9]+)$'),
         'cloudplayer.api.http.playlist_item.Entity'),
        ((r'^/playlist/(?P<playlist_provider_id>[a-z]+)'
          r'/(?P<playlist_id>[0-9a-zA-Z]+)'
          r'/item$'),
         'cloudplayer.api.http.playlist_item.Collection'),

        (r'^/playlist/(?P<provider_id>[a-z]+)/(?P<id>[0-9a-zA-Z]+)$',
         'cloudplayer.api.http.playlist.Entity'),
        (r'^/playlist/(?P<provider_id>[a-z]+)$',
         'cloudplayer.api.http.playlist.Collection'),

        ((r'^/favourite/(?P<favourite_provider_id>[a-z]+)'
          r'/(?P<favourite_id>[0-9a-zA-Z]+)'
          r'/item/(?P<id>[0-9]+)$'),
         'cloudplayer.api.http.favourite_item.Entity'),
        ((r'^/favourite/(?P<favourite_provider_id>[a-z]+)'
          r'/(?P<favourite_id>[0-9a-zA-Z]+)'
          r'/item$'),
         'cloudplayer.api.http.favourite_item.Collection'),

        (r'^/favourite/(?P<provider_id>[a-z]+)/(?P<id>[0-9a-zA-Z]+)$',
         'cloudplayer.api.http.favourite.Entity'),
        (r'^/favourite/(?P<provider_id>[a-z]+)$',
         'cloudplayer.api.http.favourite.Collection'),

        (r'^/track/(?P<provider_id>soundcloud)/(?P<id>[0-9a-zA-Z]+)$',
         'cloudplayer.api.http.track.Soundcloud'),
        (r'^/track/(?P<provider_id>youtube)/(?P<id>[0-9a-zA-Z-_]+)$',
         'cloudplayer.api.http.track.Youtube'),

        (r'^/provider$',
         'cloudplayer.api.http.provider.Collection'),
        (r'^/provider/(?P<id>[a-z]+)$',
         'cloudplayer.api.http.provider.Entity'),

        (r'^/user/(?P<id>me|[0-9]+)$',
         'cloudplayer.api.http.user.Entity'),

        (r'^/websocket$',
         'cloudplayer.api.http.socket.Handler'),

        (r'^/proxy/(soundcloud|youtube)/(.*)',
         'cloudplayer.api.http.proxy.Proxy'),

        (r'^/health_check$',
         'cloudplayer.api.http.base.HTTPHealth'),
        (r'^/.*',
         'cloudplayer.api.http.base.HTTPFallback'),
    ]

    ws_routes = [
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

        if settings.get('bugsnag'):
            bugsnag.configure(
                api_key=settings['bugsnag']['api_key'],
                project_root=settings['bugsnag']['project_root'])

        self.executor = tornado.concurrent.futures.ThreadPoolExecutor(
            settings['num_executors'])

        self.redis_pool = redis.ConnectionPool(
            host=settings['redis_host'],
            port=settings['redis_port'],
            db=settings['redis_db'],
            password=settings['redis_password'])

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
        self.session_cls = orm.sessionmaker(bind=self.engine)
        self.initialize()

    def initialize(self):
        self.ensure_tables()
        self.populate_providers()

    def ensure_tables(self):
        import cloudplayer.api.model.base as model
        model.Base.metadata.create_all(self.engine)

    def populate_providers(self):
        from cloudplayer.api.model import provider
        session = self.create_session()
        for provider_id in opt.options.providers:
            if not session.query(provider.Provider).get(provider_id):
                entity = provider.Provider(id=provider_id)
                session.add(entity)
        session.commit()
        session.close()

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
