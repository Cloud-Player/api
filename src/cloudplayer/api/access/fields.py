"""
    cloudplayer.api.access.fields
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""


class Fields(object):
    """Component for fine-tuning column-level ACL rules.

    Fields contain a set of column names that may restrict a CRUD operation.
    E.g., the owner of an entity may read more attributes than a third party.

    Column names are provided as positional arguments and can have a dotted
    syntax to describe columns of related models.
    The constructer accepts an additional target keyword to provide
    compatibility with the `Available` fields class.

    Calling a fields instance with a target entity creates a bound copy.

    The `in` operator is implemented to check whether the intent applies
    to the specified field restriction.
    """

    def __init__(self, *args, target=None):
        self._values = frozenset(args)
        self._target = target

    def __call__(self, target):
        return Fields(*self._values, target=target)

    def __iter__(self):
        yield from self._values

    def __contains__(self, item):
        if isinstance(item, Fields):
            return self._values.issuperset(item._values)
        return self._values.__contains__(item)


class Available(Fields):
    """Wildcard fields class that unlocks all fields in an ACL rule.

    Rules must reference the class uninstanciated and the target is bound
    through the constructor.
    """

    def __init__(self, target):
        self(target)

    def __call__(self, target):
        self._target = target
        self._values = frozenset()
        return self
