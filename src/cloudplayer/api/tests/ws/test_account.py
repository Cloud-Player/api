import json

import pytest

from cloudplayer.api.http.account import Entity


@pytest.mark.gen_test
def test_account_entity_should_be_available_over_websocket(user_push, account):
    message = {'channel': 'account.cloudplayer.me'}
    response = yield user_push(message)
    result = response.json()
    assert result['channel'] == 'account.cloudplayer.me'
    assert result['body']['id'] == account.id
    assert result['body']['provider_id'] == account.provider_id


@pytest.mark.gen_test
def test_account_entity_should_be_subscribable_over_websocket(
        user_push, user_fetch, db, account, monkeypatch):
    monkeypatch.setattr(Entity, 'SUPPORTED_METHODS', ('GET', 'PATCH'))
    assert account.title != 'new title'

    message = {'channel': 'account.cloudplayer.{}'.format(account.id),
               'method': 'SUB'}
    ws_resp = yield user_push(message, keep_alive=True, await_reply=False)

    http_resp = yield user_fetch(
        '/account/cloudplayer/{}'.format(account.id),
        method='PATCH', body={'title': 'new title'})
    assert http_resp.code == 200

    ws_resp = yield ws_resp.connection.read_message()
    message = json.loads(ws_resp)
    assert message['body']['title'] == 'new title'
