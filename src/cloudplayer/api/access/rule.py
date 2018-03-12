"""
    cloudplayer.api.access.rule
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.access.action import Anything
from cloudplayer.api.access.fields import Available
from cloudplayer.api.access.policy import PolicyViolation
from cloudplayer.api.access.principal import Everyone, Principal


class Grant(object):

    def __init__(self, principal=None, action=None, target=None, fields=None):
        self.principal = principal
        self.action = action
        self.target = target
        self.fields = fields


class Rule(object):

    def __init__(self, principal=Everyone, action=Anything, fields=Available):
        self.principal = principal
        self.action = action
        self.fields = fields


class Allow(Rule):

    def __call__(self, account, action, target, fields):
        grant = Grant(account, action, target, fields)

        proposed_principal = Principal(account)
        required_principal = self.principal(target)
        if required_principal != proposed_principal:
            return

        proposed_action = action(target)
        required_action = self.action(target)
        if required_action != proposed_action:
            return

        proposed_fields = fields(target)
        required_fields = self.fields(target)
        if fields is Available:
            grant.fields = required_fields
        if proposed_fields in required_fields:
            return grant


class Deny(Rule):

    def __call__(self, account, action, target, fields):
        if self.principal(target) == Principal(account):
            if self.action(target) == action(target):
                if fields(target) in self.fields(target):
                    raise PolicyViolation(403, 'operation forbidden')
