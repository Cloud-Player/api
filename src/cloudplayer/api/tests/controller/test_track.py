import pytest


@pytest.mark.gen_test
def test_soundcloud_track_controller_should_retrieve_and_convert_tracks(
        user_fetch, expect):
    response = yield user_fetch('/track/soundcloud?q=test')
    assert response.json() == expect('/tracks/soundcloud')


@pytest.mark.gen_test
def test_youtube_track_controller_should_retrieve_and_convert_tracks(
        user_fetch, expect):
    response = yield user_fetch('/track/youtube?q=test')
    assert response.json() == expect('/tracks/youtube')
