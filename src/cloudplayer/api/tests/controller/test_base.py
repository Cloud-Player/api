import pytest

from cloudplayer.api.controller.base import Controller, ControllerException


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
    with pytest.raises(ControllerException):
        Controller._merge_ids_with_kw(ids, kw)
