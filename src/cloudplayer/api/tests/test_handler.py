import pytest

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
            self.on_finish()

    class Handler(HandlerMixin, Base):
        application = app

    handler = Handler()
    trans = handler.db.begin(subtransactions=True)
    assert trans.is_active
    handler.finish()
    assert not trans.is_active
    assert handler.finished


@pytest.mark.gen_test
def test_http_handler_should_set_default_headers(http_client, base_url):
    response = yield http_client.fetch('{}/health_check'.format(base_url))
    headers = dict(response.headers)
    assert headers.pop('Date')
    assert headers.pop('Set-Cookie')
    assert headers.pop('Etag')
    assert headers.pop('Content-Length')
    assert headers == {
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Allow-Headers': 'Accept, Content-Type, Origin',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Max-Age': '600',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Content-Language': 'en-US',
        'Content-Type': 'application/json',
        'Pragma': 'no-cache',
        'Server': 'cloudplayer'}
