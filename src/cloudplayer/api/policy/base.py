"""
    cloudplayer.api.policy.base
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""


class PolicyViolation(Exception):
    pass


class PolicyFactory(object):

    def __init__(self, policies):
        name = '{}Policy'.format(p.__name__ for p in policies)
        self.policy = type(name, (BasePolicy, Mixin, *policies), {})

    def __call__(self, *args, **kw):
        return self.policy(*args, **kw)


class Mixin(object):
    pass


class BasePolicy(object):

    def __init__(self, db, current_user=None):
        self.db = db
        self.current_user = current_user

    def create(self, entity):
        self.db.add(entity)

    def read(self, model, ids):
        query = self.query(model, **ids)
        return query.one_or_none()

    def update(self, entity, **kw):
        entity.update(**kw)

    def delete(self, entity):
        self.db.delete(entity)

    def query(self, model, **kw):
        query = self.db.query(model)
        for field, value in kw.items():
            expression = getattr(model, field) == value
            query = query.filter(expression)
        return query
