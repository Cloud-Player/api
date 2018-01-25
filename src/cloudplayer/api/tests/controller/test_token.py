import pytest

from cloudplayer.api.controller.token import TokenController


@pytest.mark.gen_test
def test_controller_should_create_new_token_without_kw(db, current_user):
    controller = TokenController(db, current_user)
    token = yield controller.create({'account_id': 'ignore'}, id='ignore-too')
    assert token.id != 'ignore'
    assert token.account_id is None
    assert token.account_provider_id is None
