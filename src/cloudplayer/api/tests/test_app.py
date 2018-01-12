import pytest

import tornado.httpclient


@pytest.mark.gen_test
def test_base_route_should_return_404(http_client, base_url):
    response = yield http_client.fetch(base_url, raise_error=False)
    assert response.code == 404


@pytest.mark.gen_test
def test_unsupported_method_should_return_405(http_client, base_url):
    response = yield http_client.fetch(
        base_url, method='HEAD', raise_error=False)
    assert response.code == 405
