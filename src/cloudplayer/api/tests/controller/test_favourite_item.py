import pytest

from cloudplayer.api.controller import ControllerException
from cloudplayer.api.controller.favourite_item import FavouriteItemController


@pytest.mark.gen_test
async def test_favourite_item_controller_should_404_if_favourite_is_missing(
        db, current_user):
    controller = FavouriteItemController(db, current_user)
    ids = {'favourite_id': 'missing', 'favourite_provider_id': 'cloudplayer'}
    with pytest.raises(ControllerException) as error:
        await controller.read(ids, {'favourite_id': 'missing'})
    assert error.value.status_code == 404
