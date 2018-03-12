import pytest


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
