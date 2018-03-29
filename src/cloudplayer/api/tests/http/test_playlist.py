import pytest
from sqlalchemy.orm.util import was_deleted

from cloudplayer.api.model.playlist import Playlist
from cloudplayer.api.model.playlist_item import PlaylistItem


@pytest.mark.gen_test
def test_playlist_can_be_created(user_fetch, account):
    body = {'title': 'test playlist'}
    response = yield user_fetch(
        '/playlist/cloudplayer', method='POST', body=body)
    result = response.json()
    assert result['account_id'] == account.id
    assert result['id'] is not None
    assert result['title'] == 'test playlist'
    assert result['description'] is None


@pytest.mark.gen_test
def test_playlist_can_be_deleted_without_tracks(user_fetch):
    body = {'title': 'test playlist'}
    response = yield user_fetch(
        '/playlist/cloudplayer', method='POST', body=body)
    response = yield user_fetch('/playlist/cloudplayer/{}'.format(
        response.json()['id']), method='DELETE')
    assert response.code == 204


@pytest.mark.gen_test
def test_playlist_can_be_deleted_with_cascading_tracks(
        db, user_fetch, account):
    item = PlaylistItem(
        account=account,
        rank='aaa',
        track_id='test-id',
        track_provider_id='cloudplayer')
    playlist = Playlist(
        title='test playlist',
        provider_id='cloudplayer',
        items=[item],
        account_id=account.id,
        account_provider_id=account.provider_id)
    db.add(playlist)
    db.commit()
    item_ids = (item.id,)
    playlist_ids = (playlist.id, playlist.provider_id)

    response = yield user_fetch(
        '/playlist/cloudplayer/{}'.format(playlist.id), method='DELETE')
    assert response.code == 204

    db.expunge_all()
    assert not db.query(Playlist).get(playlist_ids)
    assert not db.query(PlaylistItem).get(item_ids)
