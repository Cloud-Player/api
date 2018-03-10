import pytest

from cloudplayer.api.controller.playlist import PlaylistController
from cloudplayer.api.model.playlist import Playlist


@pytest.mark.gen_test
def test_playlist_controller_should_resolve_random_id(db, current_user):
    playlist = Playlist(
        account_id=current_user['cloudplayer'],
        account_provider_id='cloudplayer',
        provider_id='cloudplayer',
        title='test')

    db.add(playlist)
    db.commit()
    playlist_id = playlist.id
    db.expunge(playlist)
    controller = PlaylistController(db, current_user)
    ids = {'id': 'random', 'provider_id': 'cloudplayer'}
    playlist = yield controller.read(ids)
    assert playlist.id == playlist_id
