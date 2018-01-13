import tornado.httpclient

from cloudplayer.api.handler import HandlerMixin


def test_handler_mixin_should_connect_redis_pool(app):
    class Handler(HandlerMixin):
        application = app

    handler = Handler()
    assert handler.cache.info()


def test_handler_mixin_should_provide_async_http_client():
    handler = HandlerMixin()
    base = handler.http_client.configurable_base()
    assert base is tornado.httpclient.AsyncHTTPClient


def test_handler_mixin_should_create_db_session(app):
    class Handler(HandlerMixin):
        application = app

    handler = Handler()
    assert handler.db.get_bind() is app.database.engine


def test_handler_mixin_should_close_db_on_finish(app):
    class Base(object):
        def finish(self, chunk=None):
            self.finished = True

    class Handler(HandlerMixin, Base):
        application = app

    handler = Handler()
    trans = handler.db.begin(subtransactions=True)
    assert trans.is_active
    handler.finish()
    assert not trans.is_active
    assert handler.finished
