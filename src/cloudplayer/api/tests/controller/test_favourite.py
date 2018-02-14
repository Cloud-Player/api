import pytest

from cloudplayer.api.controller.favourite import FavouriteController


@pytest.mark.gen_test
def test_favourite_controller_should_redirect_mine_alias(db, current_user):
    controller = FavouriteController(db, current_user)
    ids = {'id': 'mine', 'provider_id': 'cloudplayer'}
    favourite = yield controller.read(ids)
    assert favourite.account_id == current_user['cloudplayer']
