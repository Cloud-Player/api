"""
    cloudplayer.api.access.action
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""


class Action(object):

    def __init__(self, target=None):
        self.target = target

    def __eq__(self, other):
        raise NotImplementedError()


class Anything(Action):

    def __eq__(self, other):
        return True


class Operation(Action):

    def __eq__(self, other):
        return type(self) is type(other)


class Create(Operation):
    pass


class Read(Operation):
    pass


class Update(Operation):
    pass


class Delete(Operation):
    pass


class Query(Operation):
    pass
