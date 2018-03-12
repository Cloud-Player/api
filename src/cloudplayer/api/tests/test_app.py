import pytest
import tornado.httpclient

import cloudplayer.api.http.base
import cloudplayer.api.ws.base
import cloudplayer.api.app


@pytest.mark.gen_test
def test_base_route_should_return_404(http_client, base_url):
    response = yield http_client.fetch(base_url, raise_error=False)
    assert response.code == 404


@pytest.mark.gen_test
def test_unsupported_method_should_return_405(http_client, base_url):
    response = yield http_client.fetch(
        base_url, method='HEAD', raise_error=False)
    assert response.code == 405


def test_application_should_define_protocol_based_routing(app):
    request = tornado.httputil.HTTPServerRequest(uri='/')
    request.protocol = 'http'
    assert app.find_handler(request).handler_class is (
        cloudplayer.api.http.base.HTTPFallback)
    request.protocol = 'wss'
    assert app.find_handler(request).request_callback.func is (
        cloudplayer.api.ws.base.WSFallback)


def test_application_should_open_configured_redis_pool(app):
    assert app.redis_pool.connection_class.description_format % (
        app.redis_pool.connection_kwargs) == (
            'Connection<host=127.0.0.1,port=8869,db=0>')


def test_application_should_connect_to_configured_database(app):
    assert str(app.database.engine.url) == (
        'postgresql://postgres:@127.0.0.1:8852/postgres')


def test_database_should_create_sessions_bound_to_engine(app):
    session = app.database.create_session()
    assert session.get_bind() is app.database.engine
