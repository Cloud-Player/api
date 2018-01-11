import pytest
import sqlalchemy as sql

from cloudplayer.api.controller.base import Controller
from cloudplayer.api.model.base import Base
from cloudplayer.api.policy import Secure


def test_controller_should_store_creation_args(db, current_user):
    controller_class = type('Ctrl', (Controller,), {'__policies__': []})
    controller = controller_class(db, current_user)
    assert controller.db is db
    assert controller.current_user is current_user


def test_controller_should_generate_policy_from_class_attr(db, current_user):
    controller_class = type('Ctrl', (Controller,), {'__policies__': [Secure]})
    controller = controller_class(db, current_user)
    assert controller.policy.__class__.__name__ == 'SecurePolicy'


def test_controller_should_merge_ids_into_keywords():
    ids = {'a': 1, 'b': 2}
    kw = {'c': 3, 'd': 4}
    merged = Controller._merge_ids_into_kw(ids, **kw)
    assert merged == {'a': 1, 'b': 2, 'c': 3, 'd': 4}


def test_controller_merge_should_complain_about_conflicting_fields():
    ids = {'a': 1, 'same': 'foo'}
    kw = {'b': 2, 'same': 'bar'}
    with pytest.raises(ValueError):
        Controller._merge_ids_into_kw(ids, **kw)
