import pytest


@pytest.mark.gen_test
def test_account_entity_can_be_read_by_owner(user_fetch, account):
    response = yield user_fetch('/account/{}/me'.format(account.provider_id))
    assert response.json()['id'] == account.id
