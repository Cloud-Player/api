import sys

import mock
import pytest
import tornado.httpclient
import tornado.gen

import cloudplayer.api.handler
from cloudplayer.api import APIException
from cloudplayer.api.handler import (CollectionMixin, ControllerHandlerMixin,
                                     EntityMixin, HandlerMixin)


def test_handler_mixin_should_connect_redis_pool(app):
    class Handler(HandlerMixin):
        application = app

    handler = Handler()
    assert handler.cache.info()


def test_handler_mixin_should_provide_async_http_client():
    handler = HandlerMixin()
    base = handler.http_client.configurable_base()
    assert base is tornado.httpclient.AsyncHTTPClient


def test_handler_mixin_should_create_db_session(app):
    class Handler(HandlerMixin):
        application = app

    handler = Handler()
    assert handler.db.get_bind() is app.database.engine


def test_handler_mixin_should_close_db_on_finish(app):
    class Base(object):
        def finish(self, chunk=None):
            self.finished = True
            self.on_finish()

    class Handler(HandlerMixin, Base):
        application = app

    handler = Handler()
    trans = handler.db.begin(subtransactions=True)
    assert trans.is_active
    handler.finish()
    assert not trans.is_active
    assert handler.finished


def test_handler_should_write_errors_to_out_proto():
    class Handler(HandlerMixin):
        write = mock.MagicMock()
        _reason = 'we-are-not-gonna-take-it'

    Handler().write_error(418)
    Handler.write.assert_called_once_with(
        {'status_code': 418, 'reason': Handler._reason})


@pytest.mark.gen_test
def test_handler_should_log_api_exceptions(req, monkeypatch, base_url):
    class Handler(HandlerMixin):
        request = req

    handler = Handler()
    logger = mock.MagicMock()
    monkeypatch.setattr(cloudplayer.api.handler, 'gen_log', logger)
    try:
        raise APIException(418, 'very-bad-exception')
    except APIException:
        handler.log_exception(*sys.exc_info())

    cargs = logger.warning.call_args[0]
    expected = '418 HTTP GET %s (0.0.0.0): very-bad-exception' % base_url
    assert expected == (cargs[0] % cargs[1:])


@pytest.mark.gen_test
def test_handler_should_log_arbitrary_exceptions(req, monkeypatch, base_url):
    class Handler(HandlerMixin):
        request = req

    handler = Handler()
    logger = mock.MagicMock()
    monkeypatch.setattr(cloudplayer.api.handler, 'app_log', logger)
    try:
        raise ValueError('wild-value-error')
    except ValueError:
        handler.log_exception(*sys.exc_info())

    cargs = logger.error.call_args[0]
    expected = 'uncaught exception HTTP GET %s (0.0.0.0)' % base_url
    assert (cargs[0] % cargs[1]).startswith(expected)
    assert 'exc_info' in logger.error.call_args[1]


def test_controller_handler_mixin_should_create_controller(db, current_user):
    class ControllerHandler(ControllerHandlerMixin):
        __controller__ = mock.MagicMock(return_value=42)

        def __init__(self, db, current_user):
            self.db = db
            self.current_user = current_user

    handler = ControllerHandler(db, current_user)
    assert handler.controller == 42
    ControllerHandler.__controller__.assert_called_once_with(db, current_user)


def test_entity_mixin_supports_only_valid_methods():
    methods = {'GET', 'PUT', 'PATCH', 'DELETE'}
    assert set(EntityMixin.SUPPORTED_METHODS) == methods


class DummyHandler(object):

    def __init__(self, ctrl):
        self.__controller__ = ctrl
        self.db = None
        self.current_user = None

    @tornado.gen.coroutine
    def write(self, chunk):
        self.written = chunk

    def set_status(self, status):
        self.status = status

    def finish(self):
        self.finished = True


class DummyController(object):

    def __init__(self, db, current_user):
        self.db = db
        self.current_user = current_user

    @tornado.gen.coroutine
    def mirror(self, ids, body=None):
        return {'ids': ids, 'body': body}

    create = read = update = delete = search = mirror


@pytest.mark.gen_test
def test_entity_mixin_reads_ids_from_controller():
    handler = type('Reader', (EntityMixin, DummyHandler), {})(DummyController)
    ids = {'pkey': 'foo', 'fkey': 'bar'}
    yield handler.get(**ids)
    assert handler.written['ids'] == ids


@pytest.mark.gen_test
def test_entity_mixin_updates_body_for_ids_on_controller():
    handler = type('Updater', (EntityMixin, DummyHandler), {
        'body': '42'})(DummyController)
    ids = {'pkey': 'foo', 'fkey': 'bar'}
    yield handler.put(**ids)
    assert handler.written['ids'] == ids


@pytest.mark.gen_test
def test_entity_mixin_patches_body_for_ids_on_controller():
    handler = type('Patcher', (EntityMixin, DummyHandler), {
        'body': '42'})(DummyController)
    ids = {'pkey': 'foo', 'fkey': 'bar'}
    yield handler.patch(**ids)
    assert handler.written['ids'] == ids


@pytest.mark.gen_test
def test_entity_mixin_deletes_entity_by_ids():
    handler = type('Deleter', (EntityMixin, DummyHandler), {})(DummyController)
    ids = {'pkey': 'foo', 'fkey': 'bar'}
    yield handler.delete(**ids)
    assert handler.status == 204
    assert handler.finished


def test_collection_mixin_supports_only_valid_methods():
    methods = {'GET', 'POST'}
    assert set(CollectionMixin.SUPPORTED_METHODS) == methods


@pytest.mark.gen_test
def test_collection_mixin_creates_new_entities():
    handler = type('Creator', (CollectionMixin, DummyHandler), {
        'body': {'attrib': '73'}})(DummyController)
    ids = {'fkey': 'foo'}
    yield handler.post(**ids)
    assert handler.written['ids'] == ids
    assert handler.written['body'] == {'attrib': '73'}


@pytest.mark.gen_test
def test_collection_mixin_searches_controller():
    handler = type('Searcher', (CollectionMixin, DummyHandler), {
        'query_params': {'q': '42'}})(DummyController)
    ids = {'fkey': 'foo'}
    yield handler.get(**ids)
    assert handler.written['ids'] == ids
    assert handler.written['body'] == {'q': '42'}
