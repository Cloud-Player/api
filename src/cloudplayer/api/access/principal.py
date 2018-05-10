"""
    cloudplayer.api.access.principal
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import traceback


class Principal(object):
    """ACL component describing the actor of an intent or defined rule.

    A principal class reference is used in rules to narrow the audience
    to which the rules applies to.
    When verifing an intent, the current user is also wrapped in a principal
    instance to ensure comparability.

    The quality ooperator is implemented to check whether the intent applies
    to the specified principal definition.
    """

    def __init__(self, target):
        self._target = target

    @property
    def account(self):
        return self._target

    def __eq__(self, other):
        if isinstance(other, Principal):
            try:
                return (
                    self.account is not None and
                    other.account is not None and
                    (self.account.id == other.account.id) is True and
                    (self.account.provider_id == other.account.provider_id)
                    is True)
            except Exception:
                traceback.print_exc()
        return False


class Everyone(Principal):
    """Wildcard principal for use in rules that apply to everyone."""

    @property
    def account(self):
        return

    def __eq__(self, other):
        if isinstance(other, Principal):
            return True
        return False


class Owner(Principal):
    """Principal component that applies to the owner of its target."""

    @property
    def account(self):
        return self._target.account


class Parent(Principal):
    """Principal component applying to the owner of the target's parent."""

    @property
    def account(self):
        return self._target.parent.account


class Child(Principal):
    """Principal component that applies to the owner of a target's child.

    The only use case for the child principal are rules for the user model.
    """

    @property
    def account(self):
        return

    def __eq__(self, other):
        if isinstance(other, Principal):
            return other.account in self._target.children
        return False
