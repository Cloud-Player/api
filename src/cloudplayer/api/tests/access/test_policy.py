import mock
import pytest

from cloudplayer.api.access import Policy, PolicyViolation
from cloudplayer.api.access.action import Create, Delete, Query, Read, Update
from cloudplayer.api.access.fields import Available, Fields


def test_policy_retains_current_user_and_database(db, current_user):
    policy = Policy(db, current_user)
    assert policy.db is db
    assert policy.current_user is current_user


def test_policy_release_should_invoke_rules():
    account = mock.Mock()
    action = mock.Mock()
    target = mock.Mock()
    fields = mock.Mock()
    r1 = mock.MagicMock(return_value=None)
    r2 = mock.MagicMock(side_effect=PolicyViolation)
    target.__acl__ = (r1, r2)
    with pytest.raises(PolicyViolation):
        Policy._release(account, action, target, fields)
    r1.assert_called_once_with(account, action, target, fields)
    r2.assert_called_once_with(account, action, target, fields)


def test_policy_release_should_default_to_violation():
    rule = mock.MagicMock(return_value=None)
    target = mock.Mock()
    target.__acl__ = (rule, rule, rule)
    with pytest.raises(PolicyViolation):
        Policy._release(mock.Mock(), mock.Mock(), target, mock.Mock())


def test_policy_should_grant_create_for_available_fields():
    account = mock.Mock()
    entity = mock.Mock()
    rule = mock.MagicMock(return_value=True)
    entity.__acl__ = (rule,)
    policy = Policy(mock.Mock())
    policy.grant_create(account, entity)
    rule.assert_called_once_with(account, Create, entity, Available)


def test_policy_should_grant_read_for_available_fields():
    account = mock.Mock()
    entity = mock.Mock()
    rule = mock.MagicMock(return_value=True)
    entity.__acl__ = (rule,)
    policy = Policy(mock.Mock())
    policy.grant_read(account, entity)
    rule.assert_called_once_with(account, Read, entity, Available)


def test_policy_should_grant_update_for_specified_fields():
    account = mock.Mock()
    entity = mock.Mock()
    rule = mock.MagicMock(return_value=True)
    entity.__acl__ = (rule,)
    fields = ('one', 'two', 'six')
    policy = Policy(mock.Mock())
    policy.grant_update(account, entity, fields)
    assert rule.call_args[0][:-1] == (account, Update, entity)
    assert rule.call_args[0][-1] in Fields(*fields)


def test_policy_should_grant_delete_for_available_fields():
    account = mock.Mock()
    entity = mock.Mock()
    rule = mock.MagicMock(return_value=True)
    entity.__acl__ = (rule,)
    policy = Policy(mock.Mock())
    policy.grant_delete(account, entity)
    rule.assert_called_once_with(account, Delete, entity, Available)


def test_policy_should_grant_query_for_specified_fields():
    account = mock.Mock()
    entity = mock.Mock()
    rule = mock.MagicMock(return_value=True)
    entity.__acl__ = (rule,)
    fields = ('one', 'two', 'six')
    policy = Policy(mock.Mock())
    policy.grant_query(account, entity, fields)
    assert rule.call_args[0][:-1] == (account, Query, entity)
    assert rule.call_args[0][-1] in Fields(*fields)
