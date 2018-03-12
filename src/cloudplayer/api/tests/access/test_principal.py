import mock

from cloudplayer.api.model.account import Account
from cloudplayer.api.access.principal import (Child, Everyone, Owner, Parent,
                                              Principal)


def test_principal_should_bind_to_target():
    target = mock.Mock()
    principal = Principal(target)
    assert principal._target is target


def test_principal_should_compare_by_account_property():
    a1 = mock.Mock()
    a2 = mock.Mock()
    a1.id = a2.id = 52
    a1.provider_id = a2.provider_id = 'foo'
    p1 = Principal(a1)
    p2 = Principal(a2)
    assert p1 == p2


def test_principal_should_only_compare_to_principals():
    assert Principal(mock.Mock()) != mock.Mock()


def test_everyone_should_be_everyone():
    target = mock.Mock()
    assert Everyone(target) == Principal(target)
    assert Everyone(target) == Everyone(target)
    assert Everyone(target) == Parent(target)


def test_everyone_should_only_compare_to_principals():
    assert Everyone(mock.Mock()) != mock.Mock()


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


def test_child_should_only_compare_to_principals():
    assert Child(mock.Mock()) != mock.Mock()
