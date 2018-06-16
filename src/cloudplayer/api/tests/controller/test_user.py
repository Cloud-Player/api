import pytest

from cloudplayer.api.controller import ControllerException
from cloudplayer.api.controller.user import UserController


@pytest.mark.gen_test
async def test_controller_should_redirect_alias_to_current_user(
        db, current_user):
    controller = UserController(db, current_user)
    user = await controller.read({'id': 'me'})
    assert user.id == current_user['user_id']


@pytest.mark.gen_test
async def test_controller_should_clear_current_user_on_id_missing(
        db, current_user):
    current_user['user_id'] = 999123999456
    controller = UserController(db, current_user)
    with pytest.raises(ControllerException):
        await controller.read({'id': current_user['user_id']})
    assert current_user == {}
