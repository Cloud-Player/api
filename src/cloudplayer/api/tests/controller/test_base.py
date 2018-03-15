import mock
import pytest
import sqlalchemy.orm.util

from cloudplayer.api.access import Fields
from cloudplayer.api.controller.base import Controller, ControllerException
from cloudplayer.api.model.account import Account


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


@pytest.mark.gen_test
def test_controller_should_create_entity_and_read_result(
        db, current_user, account, user):
    controller = MyController(db, current_user, Account, mock.Mock())
    ids = {'id': '1234', 'provider_id': 'cloudplayer'}
    kw = {'title': 'foo', 'access_token': 'bar', 'user_id': user.id}
    entity = yield controller.create(ids, kw, Fields('id', 'title'))
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
