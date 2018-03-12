import sys

import mock
import pytest
import tornado.httpclient

import cloudplayer.api.handler
from cloudplayer.api import APIException
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
def test_handler_should_log_api_exceptions(req, monkeypatch, base_url):
    class Handler(HandlerMixin):
        request = req

    handler = Handler()
    logger = mock.MagicMock()
    monkeypatch.setattr(cloudplayer.api.handler, 'gen_log', logger)
    try:
        raise APIException(418, 'very-bad-exception')
    except APIException:
        handler.log_exception(*sys.exc_info())
    else:
        assert False

    cargs = logger.warning.call_args[0]
    expected = '418 HTTP GET %s (0.0.0.0): very-bad-exception' % base_url
    assert expected == (cargs[0] % cargs[1:])


@pytest.mark.gen_test
def test_handler_should_log_arbitrary_exceptions(req, monkeypatch, base_url):
    class Handler(HandlerMixin):
        request = req

    handler = Handler()
    logger = mock.MagicMock()
    monkeypatch.setattr(cloudplayer.api.handler, 'app_log', logger)
    try:
        raise ValueError('wild-value-error')
    except ValueError:
        handler.log_exception(*sys.exc_info())
    else:
        assert False

    cargs = logger.error.call_args[0]
    expected = 'uncaught exception HTTP GET %s (0.0.0.0)' % base_url
    assert (cargs[0] % cargs[1]).startswith(expected)
    assert 'exc_info' in logger.error.call_args[1]
