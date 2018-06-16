from unittest import mock

import asynctest
import pytest
import sqlalchemy.orm.util

import cloudplayer.api.controller.auth
from cloudplayer.api.access import Fields
from cloudplayer.api.controller.base import (Controller, ControllerException,
                                             ProviderRegistry)
from cloudplayer.api.model.account import Account
from cloudplayer.api.model.playlist import Playlist


def test_provider_registry_should_register_subclasses_by_provider():
    class Bar(object, metaclass=ProviderRegistry):
        def __init__(self, one, two=None):
            self.one = one
            self.two = two

    class FooBar(Bar):
        __provider__ = 'foo'

    foo_bar = Bar.for_provider('foo', 1, 2)
    assert foo_bar.one, foo_bar.two == (1, 2)


def test_controller_should_store_creation_args(db, current_user):
    controller = Controller(db, current_user)
    assert controller.db is db
    assert controller.current_user is current_user


def test_controller_should_merge_ids_into_keywords():
    ids = {'a': 1, 'b': 2}
    kw = {'c': 3, 'd': 4}
    params = Controller._merge_ids_with_kw(ids, kw)
    assert params == {'a': 1, 'b': 2, 'c': 3, 'd': 4}


def test_controller_merge_should_complain_about_conflicting_fields():
    ids = {'a': 1, 'same': 'foo'}
    kw = {'b': 2, 'same': 'bar'}
    with pytest.raises(ControllerException) as error:
        Controller._merge_ids_with_kw(ids, kw)
    assert error.value.status_code == 400


def test_controller_should_eject_ids_from_keywords():
    ids = {'a': 1, 'b': 2}
    kw = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
    params = Controller._eject_ids_from_kw(ids, kw)
    assert params == {'c': 3, 'd': 4}


def test_controller_eject_should_complain_about_conflicting_fields():
    ids = {'a': 1, 'same': 'foo'}
    kw = {'a': 1, 'b': 2, 'same': 'bar'}
    with pytest.raises(ControllerException) as error:
        Controller._eject_ids_from_kw(ids, kw)
    assert error.value.status_code == 400


class MyController(Controller):

    def __init__(self, db, cu, model, policy):
        self.db = db
        self.current_user = cu
        self.__model__ = model
        self.policy = policy


@pytest.mark.asyncio
async def test_base_controller_should_delegate_provider_fetches_to_auth_ctrls(
        db, current_user, monkeypatch):
    controller = MyController(
        db, current_user, mock.Mock(), mock.Mock())
    fetch = asynctest.CoroutineMock()
    mock_auth_controller = mock.Mock(fetch=fetch)
    for_provider = mock.MagicMock(return_value=mock_auth_controller)
    monkeypatch.setattr(cloudplayer.api.controller.auth.AuthController,
                        'for_provider', for_provider)
    params = [('sort', True)]
    await controller.fetch('foo', '/path', params=params)
    for_provider.assert_called_once_with('foo', db, current_user)
    fetch.assert_called_once_with('/path', params=params)


@pytest.mark.asyncio
async def test_controller_should_create_entity_and_read_result(
        db, current_user, account, user):
    controller = MyController(db, current_user, Account, mock.Mock())
    ids = {'id': '1234', 'provider_id': 'cloudplayer'}
    kw = {'title': 'foo', 'access_token': 'bar', 'user_id': user.id}
    entity = await controller.create(ids, kw, Fields('id', 'title'))
    assert entity.id == '1234'
    assert entity.provider_id == 'cloudplayer'
    assert entity.title == 'foo'
    assert entity.access_token == 'bar'
    assert sqlalchemy.orm.util.object_state(entity).persistent

    assert controller.policy.grant_create.call_args[0][:-1] == (
        account, entity)
    assert set(controller.policy.grant_create.call_args[0][-1]) == {
        'provider_id', 'title', 'title', 'access_token', 'id', 'user_id'}

    assert controller.policy.grant_read.call_args[0][:-1] == (
        account, entity)
    assert set(controller.policy.grant_read.call_args[0][-1]) == {
        'id', 'title'}


@pytest.mark.asyncio
async def test_controller_should_raise_bad_request_on_unknown_fields(
        db, current_user, user):
    controller = MyController(db, current_user, Account, mock.Mock())
    ids = {'id': '1234', 'provider_id': 'cloudplayer'}
    kw = {'title': 'is-good', 'foo': 'type-error', 'user_id': user.id}
    with pytest.raises(ControllerException) as error:
        await controller.create(ids, kw)
    assert error.value.status_code == 400


@pytest.mark.asyncio
async def test_controller_should_raise_bad_request_on_missing_not_null(
        db, current_user, monkeypatch):
    from sqlalchemy.sql import crud  # Silence warnings
    monkeypatch.setattr(crud.util, 'warn', mock.MagicMock())
    controller = MyController(db, current_user, Account, mock.Mock())
    ids = {'provider_id': 'cloudplayer', 'id': '3456'}
    kw = {'title': 'is-good'}
    with pytest.raises(ControllerException) as error:
        await controller.create(ids, kw)
    assert error.value.status_code == 400


@pytest.mark.asyncio
async def test_controller_should_raise_bad_request_on_mismatching_account_info(
        db, current_user, user, monkeypatch):
    controller = MyController(db, current_user, Playlist, mock.Mock())
    ids = {'provider_id': 'cloudplayer'}
    kw = {'title': 'is-good', 'user_id': current_user['user_id']}
    with pytest.raises(ControllerException) as error:
        await controller.create(ids, kw)
    assert error.value.status_code == 400


@pytest.mark.asyncio
async def test_controller_should_raise_not_found_on_failed_read(
        db, current_user):
    controller = MyController(db, current_user, Account, mock.Mock())
    ids = {'id': 'does-not-exist', 'provider_id': 'unheard-of'}
    with pytest.raises(ControllerException) as error:
        await controller.read(ids)
    assert error.value.status_code == 404


@pytest.mark.asyncio
async def test_controller_should_read_entity_by_the_books(
        db, current_user, account):
    controller = MyController(db, current_user, Account, mock.Mock())
    ids = {'id': account.id, 'provider_id': account.provider_id}
    entity = await controller.read(ids, Fields('title', 'provider_id'))
    assert entity is account

    assert controller.policy.grant_read.call_args[0][:-1] == (
        account, entity)
    assert set(controller.policy.grant_read.call_args[0][-1]) == {
        'provider_id', 'title'}


@pytest.mark.asyncio
async def test_controller_should_raise_not_found_on_failed_update(
        db, current_user):
    controller = MyController(db, current_user, Account, mock.Mock())
    ids = {'id': 'does-not-exist', 'provider_id': 'unheard-of'}
    kw = {'title': 'foo', 'refresh_token': 'bar'}
    with pytest.raises(ControllerException) as error:
        await controller.update(ids, kw, Fields('user_id', 'title'))
    assert error.value.status_code == 404


@pytest.mark.asyncio
async def test_controller_should_update_entity_and_read_result(
        db, current_user, account):
    controller = MyController(db, current_user, Account, mock.Mock())
    ids = {'id': account.id, 'provider_id': account.provider_id}
    kw = {'title': 'foo', 'refresh_token': 'bar'}
    entity = await controller.update(ids, kw, Fields('user_id', 'title'))
    assert entity is account
    assert sqlalchemy.orm.util.object_state(entity).persistent

    assert controller.policy.grant_update.call_args[0][:-1] == (
        account, entity)
    assert set(controller.policy.grant_update.call_args[0][-1]) == {
        'title', 'refresh_token'}

    assert controller.policy.grant_read.call_args[0][:-1] == (
        account, entity)
    assert set(controller.policy.grant_read.call_args[0][-1]) == {
        'user_id', 'title'}


@pytest.mark.asyncio
async def test_controller_should_raise_not_found_on_failed_delete(
        db, current_user):
    controller = MyController(db, current_user, Account, mock.Mock())
    ids = {'id': 'does-not-exist', 'provider_id': 'unheard-of'}
    with pytest.raises(ControllerException) as error:
        await controller.delete(ids)
    assert error.value.status_code == 404


@pytest.mark.asyncio
async def test_controller_should_delete_entity_and_not_return_anything(
        db, current_user, account):
    controller = MyController(db, current_user, Account, mock.Mock())
    ids = {'id': account.id, 'provider_id': account.provider_id}
    result = await controller.delete(ids)
    assert result is None
    assert sqlalchemy.orm.util.object_state(account).was_deleted

    assert controller.policy.grant_delete.call_args[0] == (
        account, account)


@pytest.mark.asyncio
async def test_controller_should_produce_model_query_with_arguments(
        db, current_user, account):
    controller = MyController(db, current_user, Account, mock.Mock())
    ids = {'provider_id': 'cloudplayer'}
    kw = {'title': 'foo'}
    query = await controller.query(ids, kw)
    assert query.statement.froms[0].name == 'account'
    assert str(query.whereclause) == (
        'account.title = :title_1 AND account.provider_id = :provider_id_1')

    assert controller.policy.grant_query.call_args[0][:-1] == (
        account, Account)
    assert set(controller.policy.grant_query.call_args[0][-1]) == {
        'title', 'provider_id'}


@pytest.mark.asyncio
async def test_controller_should_search_using_query_and_read_all_entities(
        db, current_user, account):
    controller = MyController(db, current_user, Account, mock.Mock())
    ids = {'id': account.id, 'provider_id': account.provider_id}
    entities = await controller.search(ids, {}, Fields('id'))

    assert controller.policy.grant_read.call_args[0][:-1] == (
        account, entities)
    assert set(controller.policy.grant_read.call_args[0][-1]) == {'id'}
