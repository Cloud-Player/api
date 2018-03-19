"""
    cloudplayer.api.access.action
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""


class Action(object):
    """Base class for access control list entities describing an action.

    Actions are intended by a principal and executed on a target. The target
    is bound to an action instance in its constructor.

    The equality operator is implemented to check whether the intent should
    be granted or not.
    """

    def __init__(self, target=None):
        self._target = target

    def __eq__(self, other):
        raise NotImplementedError()  # pragma: no cover


class Anything(Action):
    """Wildcard action that describes any of the below."""

    def __eq__(self, other):
        return True


class Operation(Action):
    """Base class for specific CRUD operations."""

    def __eq__(self, other):
        return type(self) is type(other)


class Create(Operation):
    """Action describing a create operation."""

    pass


class Read(Operation):
    """Action describing a read operation."""

    pass


class Update(Operation):
    """Action describing a update operation."""

    pass


class Delete(Operation):
    """Action describing a delete operation."""

    pass


class Query(Operation):
    """Action describing a query operation."""

    pass
