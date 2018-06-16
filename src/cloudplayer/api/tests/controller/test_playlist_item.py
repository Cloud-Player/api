import pytest

from cloudplayer.api.controller import ControllerException
from cloudplayer.api.controller.playlist_item import PlaylistItemController


@pytest.mark.asyncio
async def test_playlist_item_controller_should_404_if_playlist_is_missing(
        db, current_user):
    controller = PlaylistItemController(db, current_user)
    ids = {'playlist_id': 'something', 'playlist_provider_id': 'cloudplayer'}
    with pytest.raises(ControllerException) as error:
        await controller.read(ids, {'playlist_id': 'something else'})
    assert error.value.status_code == 404
