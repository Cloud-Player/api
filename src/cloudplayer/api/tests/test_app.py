import pytest

import tornado.httpclient


@pytest.mark.gen_test
def test_base_route_should_return_404(http_client, base_url):
    response = yield http_client.fetch(base_url, raise_error=False)
    assert response.code == 404


@pytest.mark.gen_test
def test_unsupported_method_should_return_405(http_client, base_url):
    request = tornado.httpclient.HTTPRequest(base_url, 'HEAD')
    response = yield http_client.fetch(request, raise_error=False)
    assert response.code == 405


@pytest.mark.gen_test
def test_http_handler_should_set_default_headers(http_client, base_url):
    response = yield http_client.fetch(
        '{}/user/me'.format(base_url), raise_error=False)
    headers = dict(response.headers)
    assert headers.pop('Date')
    assert headers.pop('Set-Cookie')
    assert headers.pop('Etag')
    assert headers.pop('Content-Length')
    assert headers == {
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Allow-Headers': 'Accept, Content-Type, Origin',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Max-Age': '600',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Content-Language': 'en-US',
        'Content-Type': 'application/json',
        'Pragma': 'no-cache',
        'Server': 'cloudplayer',
    }
