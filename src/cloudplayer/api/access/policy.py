"""
    cloudplayer.api.access.policy
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
from cloudplayer.api import APIException
from cloudplayer.api.access.action import Create, Delete, Query, Read, Update
from cloudplayer.api.access.fields import Available, Fields


class PolicyViolation(APIException):

    def __init__(self, status_code=403, log_message='operation forbidden'):
        super().__init__(status_code, log_message)


class Policy(object):

    def __init__(self, db, current_user=None):
        self.db = db
        self.current_user = current_user

    @staticmethod
    def _release(account, action, target, fields):
        for rule in target.__acl__:
            if rule(account, action, target, fields):
                return
        raise PolicyViolation()

    def grant_create(self, account, entity):
        self._release(account, Create, entity, Available)

    def grant_read(self, account, entity):
        self._release(account, Read, entity, Available)

    def grant_update(self, account, entity, fields):
        self._release(account, Update, entity, Fields(*fields))

    def grant_delete(self, account, entity):
        self._release(account, Delete, entity, Available)

    def grant_query(self, account, model, fields):
        self._release(account, Query, model, Fields(*fields))
