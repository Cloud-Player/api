from unittest import mock
import itertools

import pytest

from cloudplayer.api.access.action import Anything
from cloudplayer.api.access.fields import Available, Fields
from cloudplayer.api.access.policy import PolicyViolation
from cloudplayer.api.access.principal import Everyone
from cloudplayer.api.access.rule import Allow, Deny, Rule


def test_rule_should_bind_to_principal_action_fields_with_defaults():
    assert Rule().principal == Everyone
    assert Rule(principal='p').principal == 'p'
    assert Rule().action == Anything
    assert Rule(action='a').action == 'a'
    assert Rule().fields == Available
    assert Rule(fields='f').fields == 'f'


class ArgMocker(object):

    def __init__(self, arg):
        super().__init__()
        self.arg = arg

    def __call__(self, *_):
        return self

    def __eq__(self, *_):
        return self.arg

    def __contains__(self, *_):
        return self.arg


def test_allow_should_return_grant_if_rule_matches_else_none():
    yay = ArgMocker(True)
    nay = ArgMocker(False)
    rule = Allow(yay, yay, yay)
    account = mock.Mock()
    action = mock.MagicMock()
    target = mock.MagicMock()
    fields = Fields('one', 'four', 'eight')
    grant = rule(account, action, target, fields)
    assert grant.principal is account
    assert grant.action is action
    assert grant.target is target
    assert grant.fields is fields

    arg_list = list(itertools.product([yay, nay], repeat=3))
    arg_list.remove((yay, yay, yay))
    for args in arg_list:
        rule = Allow(*args)
        assert not rule(
            mock.Mock(), mock.MagicMock(), mock.MagicMock, mock.MagicMock())


def test_deny_should_raise_violation_if_matches_else_return_none():
    yay = ArgMocker(True)
    nay = ArgMocker(False)
    rule = Deny(yay, yay, yay)
    with pytest.raises(PolicyViolation):
        assert rule(mock.Mock(), mock.MagicMock(), None, mock.MagicMock())
    arg_list = list(itertools.product([yay, nay], repeat=3))
    arg_list.remove((yay, yay, yay))
    for args in arg_list:
        rule = Deny(*args)
        assert not rule(mock.Mock(), mock.MagicMock(), None, mock.MagicMock())
