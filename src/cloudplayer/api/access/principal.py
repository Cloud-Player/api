"""
    cloudplayer.api.access.principal
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""


class Principal(object):

    def __init__(self, target):
        self._target = target

    @property
    def account(self):
        return self._target

    def __eq__(self, other):
        if isinstance(other, Principal):
            return (
                self.account is not None and
                other.account is not None and
                (self.account.id == other.account.id) is True and
                (self.account.provider_id == other.account.provider_id)
                is True)
        return False


class Everyone(Principal):

    @property
    def account(self):
        return

    def __eq__(self, other):
        if isinstance(other, Principal):
            return True
        return False


class Owner(Principal):

    @property
    def account(self):
        return self._target.account


class Parent(Principal):

    @property
    def account(self):
        return self._target.parent.account


class Child(Principal):

    @property
    def account(self):
        return

    def __eq__(self, other):
        if isinstance(other, Principal):
            return other.account in self._target.children
        return False
