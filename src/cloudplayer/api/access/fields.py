"""
    cloudplayer.api.access.fields
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""


class Fields(object):

    def __init__(self, *args):
        self._target = None
        self._values = frozenset(args)

    def __call__(self, target):
        self._target = target
        return self

    def __iter__(self):
        yield from self._values

    def __contains__(self, item):
        if isinstance(item, Fields):
            return self._values.issuperset(item._values)
        return self._values.__contains__(item)


class Available(Fields):

    def __init__(self, target):
        self(target)

    def __call__(self, target):
        self._target = target
        self._values = frozenset(target.__fields__)
        return self


class _Empty(Fields):

    def __init__(self):
        self._target = None
        self._values = frozenset()

    def __call__(self, *args):
        return self


Empty = _Empty()
