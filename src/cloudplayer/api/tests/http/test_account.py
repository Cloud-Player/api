import pytest


@pytest.mark.gen_test
def test_account_entity_can_be_read_by_owner(user_fetch, account):
    response = yield user_fetch('/account/{}/me'.format(account.provider_id))
    assert response.json()['id'] == account.id


@pytest.mark.gen_test
def test_account_returns_all_fields_for_owner(user_fetch, account):
    response = yield user_fetch('/account/{}/{}'.format(
        account.provider_id, account.id))
    result = response.json()
    assert set(result.pop('image').keys()) == {
        'id',
        'small',
        'medium',
        'large'}
    assert set(result.keys()) == {
        'id',
        'provider_id',
        'user_id',
        'connected',
        'favourite_id',
        'title',
        'created',
        'updated'}


@pytest.mark.gen_test
def test_account_returns_limited_fields_for_others(user_fetch, other):
    response = yield user_fetch('/account/{}/{}'.format(
        other.provider_id, other.id))
    result = response.json()
    assert set(result.pop('image').keys()) == {
        'id',
        'small',
        'medium',
        'large'}
    assert set(result.keys()) == {
        'id',
        'provider_id',
        'title'}
