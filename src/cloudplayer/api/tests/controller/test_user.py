import pytest

from cloudplayer.api.controller.user import UserController


@pytest.mark.gen_test
def test_controller_should_redirect_alias_to_current_user(db, current_user):
    controller = UserController(db, current_user)
    user = yield controller.read({'id': 'me'})
    assert user.id == current_user['user_id']
