import pytest


@pytest.mark.gen_test
def test_account_entity_should_be_available_over_websocket(user_push, account):
    message = {'channel': 'account.cloudplayer.me'}
    response = yield user_push(message)
    result = response.json()
    assert result['channel'] == 'account.cloudplayer.me'
    assert result['body']['id'] == account.id
    assert result['body']['provider_id'] == account.provider_id


@pytest.mark.skip(reason='race condition needs resolving')
@pytest.mark.gen_test(run_sync=False)
def test_account_entity_should_be_subscribable_over_websocket(
        user_push, user_fetch, delay, db, account):
    message = {'channel': 'account.cloudplayer.{}'.format(account.id),
               'method': 'SUB'}
    response = yield user_push(message, keep_alive=True)
    assert response.json()['body']['status'] == 200

    response = yield user_fetch(
        '/account/cloudplayer/{}'.format(account.id),
        method='PATCH', body={'title': 'new title'})

    message = yield response.connection.read_message()
    assert message == {}
