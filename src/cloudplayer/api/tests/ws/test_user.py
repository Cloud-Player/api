import pytest


@pytest.mark.gen_test
def test_user_entity_should_be_available_over_websocket(user_push, user):
    response = yield user_push({'channel': 'user.me'})
    result = response.json()
    assert result['channel'] == 'user.me'
    assert result['body']['id'] == str(user.id)
    assert result['body'].pop('accounts')
