"""
    cloudplayer.api.access.fields
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""


class Fields(object):

    def __init__(self, *args):
        self.target = None
        self.values = frozenset(args)

    def __iter__(self):
        if self.values:
            yield from self.values

    def __call__(self, target):
        self.target = target
        return self

    def __contains__(self, item):
        if isinstance(item, Fields):
            return self.values.issuperset(item)
        return self.values.__contains__(item)


class Available(Fields):

    def __init__(self, target):
        self(target)

    def __call__(self, target):
        self.target = target
        self.values = frozenset(target.__fields__)
        return self


Empty = Fields()
