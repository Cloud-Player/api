import json

from unittest import mock
import asynctest
import pytest
import tornado.web

from cloudplayer.api.http.auth import AuthHandler, Soundcloud, Youtube


@pytest.mark.asyncio
async def test_soundcloud_auth_redirects_with_arguments(
        base_url, http_client):
    future = http_client.fetch(
        '{}/soundcloud'.format(base_url),
        follow_redirects=False, raise_error=False)
    import tornado.gen
    response = await tornado.gen.convert_yielded(future)
    assert response.headers['Location'] == (
        'https://soundcloud.com/connect?'
        'redirect_uri=sc.to%2Fauth&'
        'client_id=sc-key&'
        'response_type=code&'
        'state=testing')


@pytest.mark.asyncio
async def test_youtube_auth_redirects_with_arguments(base_url, http_client):
    response = await http_client.fetch(
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
async def test_auth_handler_redirects_to_close_html_on_provider_callback(
        base_url, http_client, monkeypatch, provider_id):
    callback = asynctest.CoroutineMock()
    monkeypatch.setattr(AuthHandler, 'provider_callback', callback)
    response = yield http_client.fetch(
        '{}/{}?code=42'.format(base_url, provider_id),
        follow_redirects=False, raise_error=False)
    assert response.headers['Location'] == '/static/close.html'
    callback.assert_called_once()


@pytest.mark.gen_test
async def test_auth_handler_closes_with_html_even_on_callback_failure(
        base_url, http_client, monkeypatch):
    callback = asynctest.CoroutineMock(side_effect=tornado.web.HTTPError(400))
    monkeypatch.setattr(AuthHandler, 'provider_callback', callback)
    response = yield http_client.fetch(
        '{}/soundcloud?code=42'.format(base_url),
        follow_redirects=False, raise_error=False)
    assert response.headers['Location'] == '/static/close.html'
    callback.assert_called_once()


@pytest.mark.asyncio
async def test_auth_handler_should_fetch_soundcloud_user_with_body(
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
    response = mock.Mock()

    async def fetch(*args, **kw):
        response.body = json.dumps(responses.pop(0))
        return response

    mock_client = mock.MagicMock(fetch=fetch)
    monkeypatch.setattr(Soundcloud, 'http_client', mock_client)

    response = await http_client.fetch(
        '{}/soundcloud?code=42'.format(base_url),
        follow_redirects=False, raise_error=False)
    assert 'tok_v1' in response.headers['Set-Cookie']


@pytest.mark.asyncio
async def test_auth_handler_should_fetch_youtube_user_with_body(
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
    response = mock.Mock()

    async def fetch(*args, **kw):
        response.body = json.dumps(responses.pop(0))
        return response

    mock_client = mock.MagicMock(fetch=fetch)
    monkeypatch.setattr(Youtube, 'http_client', mock_client)

    response = await http_client.fetch(
        '{}/youtube?code=42'.format(base_url),
        follow_redirects=False, raise_error=False)
    assert 'tok_v1' in response.headers['Set-Cookie']
