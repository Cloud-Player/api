import pytest
import sqlalchemy.orm.util

from cloudplayer.api.controller.playlist import PlaylistController
from cloudplayer.api.model.playlist import Playlist


@pytest.mark.asyncio
async def test_playlist_controller_should_resolve_random_id(db, current_user):
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
    playlist = await controller.read(ids)
    assert playlist.id == playlist_id


@pytest.mark.asyncio
async def test_playlist_controller_should_create_entity_and_read_result(
        db, current_user, account, user):
    controller = PlaylistController(db, current_user)
    ids = {'provider_id': 'cloudplayer'}
    kw = {'title': 'foo', 'account_id': account.id,
          'account_provider_id': account.provider_id}
    entity = await controller.create(ids, kw)
    assert isinstance(entity.id, str)
    assert entity.provider_id == 'cloudplayer'
    assert entity.title == 'foo'
    assert entity.account is account
    assert sqlalchemy.orm.util.object_state(entity).persistent
