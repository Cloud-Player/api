"""
    cloudplayer.api.controller.base
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by Nicolas Drebenstedt
    :license: GPL-3.0, see LICENSE for details
"""
import sqlalchemy.exc
import tornado.gen
from tornado.log import app_log

from cloudplayer.api import APIException
from cloudplayer.api.access import Available, Policy


class ControllerException(APIException):

    def __init__(self, status_code=400, log_message='controller exception'):
        super().__init__(status_code, log_message)


class ProviderRegistry(type):
    """Metaclass for controllers that registers provider specific
    implementations on the generic controller under the provider ID.

    It adds a `for_provider` class method to the generic controller,
    which acts as a instance factory for provider specific controllers.
    """

    def __init__(cls, name, bases, classdict):
        if classdict.get('__provider__'):
            provider = classdict['__provider__']
            for base in bases:
                base.__registry__[provider] = cls
                app_log.debug(
                    '{} is providing {} for {}'.format(
                        name, provider, base.__name__))
        elif '__registry__' not in classdict:
            def for_provider(cls, provider_id, *args, **kw):
                """Create a specialized controller for a given `provider_id`.
                Any further arguments are passed through to the constructor.
                """
                if provider_id in cls.__registry__:
                    return cls.__registry__[provider_id](*args, **kw)
                raise ValueError('unsupported provider')
            cls.for_provider = classmethod(for_provider)
            cls.__registry__ = {}
            app_log.debug('{} is base controller'.format(name))
        type.__init__(cls, name, bases, classdict)


class Controller(object, metaclass=ProviderRegistry):
    """Protocol agnostic base controller to fulfill CRUD on model classes.

    Implementations provide a model class attribute that allow CRUD methods
    to dynamically adapt to the models field an ACL definitions.
    """

    __model__ = None

    def __init__(self, db, current_user=None, pubsub=None):
        self.db = db
        self.pubsub = pubsub
        self.current_user = current_user
        self.policy = Policy(db, current_user)

    @staticmethod
    def _merge_ids_with_kw(ids, kw):
        params = kw.copy()
        for field, value in ids.items():
            if field in params and params[field] != value:
                # TODO: Could this error expose entity existance?
                raise ControllerException(400, 'mismatch on {}'.format(field))
            params[field] = value
        return params

    @staticmethod
    def _eject_ids_from_kw(ids, kw):
        params = kw.copy()
        for field, value in ids.items():
            if field in params:
                if params[field] == value:
                    del params[field]
                else:
                    # TODO: Could this error expose entity existance?
                    raise ControllerException(
                        400, 'mismatch on {}'.format(field))
        return params

    @tornado.gen.coroutine
    def fetch(self, provider_id, path, params=None, **kw):
        """Convenience method for fetching from an upstream provider."""
        # TODO: Can authed fetching be generalized?
        from cloudplayer.api.controller.auth import AuthController
        controller = AuthController.for_provider(
            provider_id, self.db, self.current_user)
        response = yield controller.fetch(path, params=params, **kw)
        return response

    def get_account(self, provider_id):
        from cloudplayer.api.model.account import Account
        if not hasattr(self, '_accounts'):
            self._accounts = {}
        if provider_id not in self._accounts:
            account = self.db.query(Account).get((
                self.current_user[provider_id],
                provider_id))
            self._accounts[provider_id] = account
        return self._accounts[provider_id]

    @tornado.gen.coroutine
    def create(self, ids, kw, fields=Available):
        provider_id = ids.get('provider_id', 'cloudplayer')
        account = self.get_account(provider_id)

        if account and self.__model__.requires_account():
            kw.setdefault('account_id', account.id)
            kw.setdefault('account_provider_id', account.provider_id)

        params = self._merge_ids_with_kw(ids, kw)
        try:
            entity = self.__model__(**params)
            self.db.add(entity)
            entity = self.db.merge(entity)
        except TypeError as error:
            raise ControllerException(400, 'consistency error %s' % error)
        except sqlalchemy.exc.IntegrityError as error:
            message = error.orig.diag.message_primary
            raise ControllerException(400, 'integrity error %s' % message)
        self.policy.grant_create(account, entity, params.keys())
        self.db.commit()
        self.policy.grant_read(account, entity, fields)
        return entity

    @tornado.gen.coroutine
    def read(self, ids, fields=Available):
        entity = self.db.query(self.__model__).filter_by(**ids).first()
        if not entity:
            raise ControllerException(404, 'entity not found')
        account = self.get_account(entity.provider_id)
        self.policy.grant_read(account, entity, fields)
        return entity

    @tornado.gen.coroutine
    def update(self, ids, kw, fields=Available):
        entity = self.db.query(self.__model__).filter_by(**ids).first()
        if not entity:
            raise ControllerException(404, 'updatable not found')
        account = self.get_account(entity.provider_id)
        self.policy.grant_read(account, entity, fields)
        params = self._eject_ids_from_kw(ids, kw)
        self.policy.grant_update(account, entity, params)
        for field, value in params.items():
            setattr(entity, field, value)
        self.db.commit()
        return entity

    @tornado.gen.coroutine
    def delete(self, ids):
        entity = self.db.query(self.__model__).filter_by(**ids).first()
        if not entity:
            raise ControllerException(404, 'deletable not found')
        account = self.get_account(entity.provider_id)
        self.policy.grant_delete(account, entity)
        self.db.delete(entity)
        self.db.commit()

    @tornado.gen.coroutine
    def query(self, ids, kw):
        provider_id = ids.get('provider_id', 'cloudplayer')
        account = self.get_account(provider_id)
        if 'account_id' in kw:
            kw.setdefault('account_provider_id', provider_id)
        params = self._merge_ids_with_kw(ids, kw)
        self.policy.grant_query(account, self.__model__, params)
        query = self.db.query(self.__model__)
        for field, value in params.items():
            expression = getattr(self.__model__, field) == value
            query = query.filter(expression)
        return query

    @tornado.gen.coroutine
    def search(self, ids, kw, fields=Available):
        query = yield self.query(ids, kw)
        entities = query.all()
        provider_id = ids.get('provider_id', 'cloudplayer')
        account = self.get_account(provider_id)
        self.policy.grant_read(account, entities, fields)
        return entities

    @tornado.gen.coroutine
    def sub(self, ids, registry):
        provider_id = ids.get('provider_id', 'cloudplayer')
        account = self.get_account(provider_id)
        kw = {}
        if account and self.__model__.requires_account():
            kw.setdefault('account_id', account.id)
            kw.setdefault('account_provider_id', account.provider_id)
        params = self._merge_ids_with_kw(ids, kw)
        self.policy.grant_query(account, self.__model__, params)
        self.pubsub.subscribe(**registry)

    @tornado.gen.coroutine
    def unsub(self, ids, registry):
        for channel in registry:
            self.pubsub.subscribe(channel)
