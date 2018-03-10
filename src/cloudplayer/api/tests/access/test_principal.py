import mock

from cloudplayer.api.model.account import Account
from cloudplayer.api.access.principal import (Child, Everyone, Owner, Parent,
                                              Principal)


def test_principal_should_bind_to_target():
    target = mock.Mock()
    principal = Principal(target)
    assert principal._target is target


def test_everyone_should_be_everyone():
    target = mock.Mock()
    assert Everyone(target) == Principal(target)
    assert Everyone(target) == Everyone(target)
    assert Everyone(target) == Parent(target)


def test_ownership_should_be_inferred_by_account_property():
    account = Account(id=55)
    target = mock.Mock()
    target.account = account
    assert Owner(target) == Principal(account)
    assert Owner(target) != Principal(Account(id=99))


def test_parenthood_should_be_inferred_by_parent_property():
    account = Account(id=13)
    target = mock.Mock()
    target.parent.account = account
    assert Parent(target) == Principal(account)
    assert Parent(target) != Principal(Account(id=99))


def test_descendancy_should_be_inferred_by_children_property():
    account = Account(id=13)
    target = mock.Mock()
    target.children = [account]
    assert Child(target) == Principal(account)
    assert Child(target) != Principal(Account(id=99))
