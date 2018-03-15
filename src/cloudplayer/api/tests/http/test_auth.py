import json

import mock
import pytest
import tornado.gen
import tornado.web

from cloudplayer.api.http.auth import AuthHandler, Soundcloud, Youtube


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


@pytest.mark.gen_test
def test_auth_handler_should_fetch_soundcloud_user_with_body(
        base_url, http_client, monkeypatch):
    responses = [{
        'access_token': '1234',
        'expires_in': 21599,
        'scope': '*',
        'refresh_token': '1234'
    }, {
        'id': 1234,
        'avatar_url': 'img.co/large.jpg',
        'username': 'foo bar'
    }]

    @tornado.gen.coroutine
    def fetch(*args, **kw):
        response = mock.Mock()
        response.body = json.dumps(responses.pop(0))
        return response

    mock_client = mock.MagicMock(fetch=fetch)
    monkeypatch.setattr(Soundcloud, 'http_client', mock_client)

    response = yield http_client.fetch(
        '{}/soundcloud?code=42'.format(base_url),
        follow_redirects=False, raise_error=False)
    assert 'tok_v1' in response.headers['Set-Cookie']


@pytest.mark.gen_test
def test_auth_handler_should_fetch_youtube_user_with_body(
        base_url, http_client, monkeypatch):
    responses = [{
        'access_token': '1234',
        'token_type': 'Bearer',
        'expires_in': 3599,
        'id_token': '1234',
        'refresh_token': '1234'
    }, {
        'id': 'xyz',
        'snippet': {
            'thumbnails': {
                'default': {'url': 'img.xy/default.jpg'},
                'medium': {'url': 'img.xy/medium.jpg'},
                'high': {'url': 'img.xy/high.jpg'}},
            'title': 'foo bar'
        }
    }]

    @tornado.gen.coroutine
    def fetch(*args, **kw):
        response = mock.Mock()
        response.body = json.dumps(responses.pop(0))
        return response

    mock_client = mock.MagicMock(fetch=fetch)
    monkeypatch.setattr(Youtube, 'http_client', mock_client)

    response = yield http_client.fetch(
        '{}/youtube?code=42'.format(base_url),
        follow_redirects=False, raise_error=False)
    assert 'tok_v1' in response.headers['Set-Cookie']
