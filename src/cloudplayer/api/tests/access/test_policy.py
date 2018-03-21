import mock
import pytest
import sqlalchemy as sql

from cloudplayer.api.access.action import Create, Delete, Query, Read, Update
from cloudplayer.api.access.fields import Available, Fields
from cloudplayer.api.access.policy import Policy, PolicyViolation
from cloudplayer.api.access.rule import Grant
from cloudplayer.api.model import Base


def test_policy_grant_should_invoke_rules():
    account = mock.Mock()
    action = mock.Mock(__call__=lambda s, _: s)
    target = mock.Mock(__call__=lambda s, _: s)
    fields = Fields('one', 'two', 'three')
    r1 = mock.MagicMock(return_value=None)
    r2 = mock.MagicMock(side_effect=PolicyViolation)
    target.__acl__ = (r1, r2)
    with pytest.raises(PolicyViolation):
        Policy.grant(account, action, target, fields)
    r1.assert_called_once_with(account, action, target, fields)
    r2.assert_called_once_with(account, action, target, fields)


def test_policy_grant_should_default_to_violation():
    rule = mock.MagicMock(return_value=None)
    target = mock.Mock()
    target.__acl__ = (rule, rule, rule)
    with pytest.raises(PolicyViolation):
        Policy.grant(mock.Mock(), mock.Mock(), target, Available)


def test_policy_should_grant_create_for_available_fields():
    account = mock.Mock()
    entity = mock.Mock()
    grant = Grant(account, Create, entity, Available)
    rule = mock.MagicMock(return_value=grant)
    entity.__acl__ = (rule,)
    policy = Policy(None, None)
    policy.grant_create(account, entity, Available)
    rule.assert_called_once_with(account, Create, entity, Available)


def test_policy_should_grant_read_for_available_fields():
    account = mock.Mock()
    entity = mock.Mock()
    grant = Grant(account, Read, entity, Available)
    rule = mock.MagicMock(return_value=grant)
    entity.__acl__ = (rule,)
    policy = Policy(None, None)
    policy.grant_read(account, entity, Available)
    rule.assert_called_once_with(account, Read, entity, Available)


def test_policy_should_grant_update_for_specified_fields():
    account = mock.Mock()
    entity = mock.Mock()
    fields = Fields('one', 'two', 'six')
    grant = Grant(account, Update, entity, fields)
    rule = mock.MagicMock(return_value=grant)
    entity.__acl__ = (rule,)
    fields = ('one', 'two', 'six')
    policy = Policy(None, None)
    policy.grant_update(account, entity, fields)
    assert rule.call_args[0][:-1] == (account, Update, entity)
    assert rule.call_args[0][-1] in Fields(*fields)


def test_policy_should_grant_delete_for_available_fields():
    account = mock.Mock()
    entity = mock.Mock()
    grant = Grant(account, Delete, entity, Available)
    rule = mock.MagicMock(return_value=grant)
    entity.__acl__ = (rule,)
    policy = Policy(None, None)
    policy.grant_delete(account, entity)
    rule.assert_called_once_with(account, Delete, entity, Available)


class MyModel(Base):
    one = sql.Column(sql.Integer, primary_key=True)
    two = sql.Column(sql.Integer)
    six = sql.Column(sql.Integer)


def test_policy_should_grant_query_for_specified_fields(db):
    account = mock.Mock()
    fields = Fields('one', 'two', 'six')
    grant = Grant(account, Query, MyModel, fields)
    rule = mock.MagicMock(return_value=grant)
    MyModel.__acl__ = (rule,)
    kw = {'one': 1, 'two': 2, 'six': 6}
    policy = Policy(db, None)
    policy.grant_query(account, MyModel, kw)
    c_principal, c_action, c_target, c_fields = rule.call_args[0]
    assert c_principal == account
    assert c_action == Query
    assert isinstance(c_target, MyModel)
    assert c_fields in Fields(*fields)
