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
    """Operator class that can verify the compliance of CRUD operations.

    An intent is passed as a method call and a grant is issued upon compliance
    or a violancion exception is raised on dissent.
    """

    def __init__(self, db, current_user):
        self.db = db
        self.current_user = current_user

    @staticmethod
    def grant(account, action, target, fields):
        if fields is not Available and not isinstance(fields, Fields):
            fields = Fields(*fields)
        for rule in target.__acl__:
            grant = rule(account, action, target, fields)
            if grant:
                return grant
        raise PolicyViolation(404, 'no grant issued')

    def grant_create(self, account, entity, fields):
        grant = self.grant(account, Create, entity, fields)
        entity.fields = grant.fields
        return grant

    def grant_read(self, account, entity_or_entities, fields):
        # TODO: Find a better way to grant multi reads
        if isinstance(entity_or_entities, list):
            return self._grant_multi_read(account, entity_or_entities, fields)
        else:
            return self._grant_solo_read(account, entity_or_entities, fields)

    def _grant_solo_read(self, account, entity, fields):
        grant = self.grant(account, Read, entity, fields)
        entity.fields = grant.fields
        return grant

    def _grant_multi_read(self, account, entities, fields):
        grants = []
        for entity in entities:
            grant = self._grant_solo_read(account, entity, fields)
            grants.append(grant)
        return grants

    def grant_update(self, account, entity, fields):
        grant = self.grant(account, Update, entity, fields)
        entity.fields = grant.fields
        return grant

    def grant_delete(self, account, entity):
        return self.grant(account, Delete, entity, Available)

    def grant_query(self, account, model, query):
        template = model(**query)
        self.db.enable_relationship_loading(template)
        grant = self.grant(account, Query, template, query.keys())
        self.db.expunge(template)
        grant.target = model
        return grant
