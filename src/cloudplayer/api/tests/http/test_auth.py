import mock
import pytest
import tornado.gen
import tornado.web

from cloudplayer.api.http.auth import AuthHandler


@pytest.mark.gen_test
def test_soundcloud_auth_redirects_with_arguments(base_url, http_client):
    response = yield http_client.fetch(
        '{}/soundcloud'.format(base_url),
        follow_redirects=False, raise_error=False)
    assert response.headers['Location'] == (
        'https://soundcloud.com/connect?'
        'redirect_uri=sc.to%2Fauth&'
        'client_id=sc-key&'
        'response_type=code&'
        'state=testing')


@pytest.mark.gen_test
def test_youtube_auth_redirects_with_arguments(base_url, http_client):
    response = yield http_client.fetch(
        '{}/youtube'.format(base_url),
        follow_redirects=False, raise_error=False)
    assert response.headers['Location'] == (
        'https://accounts.google.com/o/oauth2/auth?'
        'redirect_uri=yt.to%2Fauth&'
        'client_id=yt-key&'
        'response_type=code&'
        'approval_prompt=auto&'
        'access_type=offline&'
        'scope=profile+email+'
        'https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fyoutube')


@pytest.mark.parametrize('provider_id', ['soundcloud', 'youtube'])
@pytest.mark.gen_test
def test_auth_handler_redirects_to_close_html_on_provider_callback(
        base_url, http_client, monkeypatch, provider_id):
    callback = mock.MagicMock()
    routine = tornado.gen.coroutine(callback)
    monkeypatch.setattr(AuthHandler, 'provider_callback', routine)
    response = yield http_client.fetch(
        '{}/{}?code=42'.format(base_url, provider_id),
        follow_redirects=False, raise_error=False)
    assert response.headers['Location'] == '/static/close.html'
    callback.assert_called_once()


@pytest.mark.gen_test
def test_auth_handler_closes_with_html_even_on_callback_failure(
        base_url, http_client, monkeypatch):
    callback = mock.MagicMock(side_effect=tornado.web.HTTPError(400))
    routine = tornado.gen.coroutine(callback)
    monkeypatch.setattr(AuthHandler, 'provider_callback', routine)
    response = yield http_client.fetch(
        '{}/soundcloud?code=42'.format(base_url),
        follow_redirects=False, raise_error=False)
    assert response.headers['Location'] == '/static/close.html'
    callback.assert_called_once()
