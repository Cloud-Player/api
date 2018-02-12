"""
    cloudplayer.api.access.rule
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api.access.action import Anything
from cloudplayer.api.access.fields import Available
from cloudplayer.api.access.policy import PolicyViolation
from cloudplayer.api.access.principal import Everyone


class Rule(object):

    def __init__(self, principal=Everyone, action=Anything, fields=Available):
        self.principal = principal
        self.action = action
        self.fields = fields

    def __call__(self, principal, action, fields):
        raise NotImplementedError()


class Allow(Rule):

    def __call__(self, principal, action, target, fields):
        if self.principal(target) == principal:
            if self.action(target) == action(target):
                if fields(target) in self.fields(target):
                    return True


class Deny(Rule):

    def __call__(self, principal, action, target, fields):
        if self.principal(target) == principal:
            if self.action(target) == action(target):
                if fields(target) in self.fields(target):
                    raise PolicyViolation(404)
