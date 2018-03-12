import mock
import pytest
import tornado.web

from cloudplayer.api.http.base import HTTPFallback, HTTPHandler, HTTPHealth


def test_http_handler_supports_relevant_methods(app, req):
    methods = {'GET', 'POST', 'PATCH', 'DELETE', 'OPTIONS'}
    assert set(HTTPHandler.SUPPORTED_METHODS) == methods
    method_string = HTTPHandler(app, req).allowed_methods
    assert set(method_string.split(', ')) == methods


def test_http_handler_stores_init_vars(app, req):
    handler = HTTPHandler(app, req)
    assert handler.application is app
    assert handler.request is req
    assert handler.current_user is None
    assert handler.original_user is None


@pytest.mark.gen_test
def test_http_fallback_throws_404_for_get_405_for_others(app, req):
    handler = HTTPFallback(app, req)
    with pytest.raises(tornado.web.HTTPError) as error:
        yield handler.get()
    assert error.value.status_code == 404

    with pytest.raises(tornado.web.HTTPError) as error:
        yield handler.post()
    assert error.value.status_code == 405


@pytest.mark.gen_test
def test_http_health_should_query_redis_and_postgres(app, req, monkeypatch):
    handler = HTTPHealth(app, req)
    info = mock.MagicMock()
    monkeypatch.setattr(handler.cache, 'info', info)
    execute = mock.MagicMock()
    monkeypatch.setattr(handler.db, 'execute', execute)
    handler._transforms = []
    yield handler.get()
    info.assert_called_once_with('server')
    execute.assert_called_once_with('SELECT 1 = 1;')
