"""
    cloudplayer.api.access.principal
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""


class Principal(object):

    def __init__(self, target):
        self._target = target

    def __eq__(self, other):
        raise NotImplementedError()  # pragma: no cover


class Everyone(Principal):

    def __eq__(self, other):
        return True


class Owner(Principal):

    def __eq__(self, other):
        return self._target.account == other


class Parent(Principal):

    def __eq__(self, other):
        return self._target.parent == other


class Child(Principal):

    def __eq__(self, other):
        return other in self._target.children
