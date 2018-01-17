from cloudplayer.api.controller.token import TokenController


def test_controller_should_create_new_token_without_kw(db, current_user):
    controller = TokenController(db, current_user)
    token = controller.create({'account_id': 'ignore'}, id='ignore-even-more')
    assert token.id != 'ignore'
    assert token.account_id is None
    assert token.account_provider_id is None
