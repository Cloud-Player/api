import datetime
import hashlib
import json

import mock
import pytest
import sqlalchemy.orm.util
import tornado.gen

from cloudplayer.api.controller import ControllerException
from cloudplayer.api.controller.auth import (
    AuthController, SoundcloudAuthController, YoutubeAuthController)
from cloudplayer.api.model.account import Account
from cloudplayer.api.model.image import Image


@pytest.mark.parametrize('id_, class_', [
    ('soundcloud', SoundcloudAuthController),
    ('youtube', YoutubeAuthController)])
def test_controller_for_provider_should_return_correct_controller(id_, class_):
    controller = AuthController.for_provider(id_, mock.Mock())
    assert isinstance(controller, class_)


def test_controller_for_provider_should_reject_invalid_provider_id():
    with pytest.raises(ValueError):
        AuthController.for_provider('not-a-provider', mock.Mock())


class CloudplayerController(AuthController):
    PROVIDER_ID = 'cloudplayer'
    OAUTH_ACCESS_TOKEN_URL = 'cp://auth'
    API_BASE_URL = 'cp://base-api'
    OAUTH_TOKEN_PARAM = 'token-param'
    OAUTH_CLIENT_KEY = 'client-key'

    def _update_account_profile(self, account_info):
        self.account.title = account_info['title']
        self.account.image = account_info['image']


def test_auth_controller_should_provide_instance_args(db, current_user):
    controller = CloudplayerController(db, current_user)
    assert controller.db is db
    assert controller.current_user == current_user
    assert controller.settings == {
        'api_key': 'cp-api-key',
        'key': 'cp-key',
        'redirect_uri': 'cp.to/auth',
        'secret': 'cp-secret'}
    assert controller.account.id == current_user['cloudplayer']


def test_auth_controller_should_check_token_expiration_before_refresh(
        db, current_user):
    controller = CloudplayerController(db, current_user)
    a_second_ago = datetime.datetime.utcnow() - datetime.timedelta(seconds=1)
    controller.account.token_expiration = a_second_ago
    assert controller._should_refresh is True
    in_an_hour = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    controller.account.token_expiration = in_an_hour
    assert controller._should_refresh is False


@pytest.mark.gen_test
def test_auth_controller_should_raise_403_on_refresh_error(
        db, current_user):

    ages_ago = datetime.datetime(2015, 7, 14, 12, 30)
    controller = CloudplayerController(db, current_user)
    account = controller.account
    account.access_token = 'stale-access-token'
    account.refresh_token = 'stale-refresh-token'
    account.token_expiration = ages_ago

    @tornado.gen.coroutine
    def fetch(*_, **kw):
        response = mock.Mock()
        response.error = True
        return response

    with mock.patch.object(controller.http_client, 'fetch', fetch):
        with pytest.raises(ControllerException) as error:
            yield controller._refresh_access()
    assert error.value.status_code == 403


@pytest.mark.parametrize('body, expect', [
    ({
        'access_token': 'new-access-token'
    }, {
        'access_token': 'new-access-token',
        'refresh_token': 'old-refresh-token',
        'token_expiration': datetime.datetime(2015, 7, 14, 12, 30)
    }),
    ({
        'access_token': 'new-access-token',
        'refresh_token': 'new-refresh-token'
    }, {
        'access_token': 'new-access-token',
        'refresh_token': 'new-refresh-token',
        'token_expiration': datetime.datetime(2015, 7, 14, 12, 30)
    }),
    ({
        'access_token': 'new-access-token',
        'refresh_token': 'new-refresh-token',
        'expires_in': 300,
    }, {
        'access_token': 'new-access-token',
        'refresh_token': 'new-refresh-token',
        'token_expiration': (
            datetime.datetime.utcnow() + datetime.timedelta(seconds=300))
    })
])
@pytest.mark.gen_test
def test_auth_controller_should_refresh_access_token(
        db, current_user, body, expect):

    controller = CloudplayerController(db, current_user)
    account = controller.account
    account.access_token = 'old-access-token'
    account.refresh_token = 'old-refresh-token'
    account.token_expiration = datetime.datetime(2015, 7, 14, 12, 30)

    @tornado.gen.coroutine
    def fetch(*_, **kw):
        response = mock.Mock()
        response.error = None
        response.body = json.dumps(body)
        return response

    with mock.patch.object(controller.http_client, 'fetch', fetch):
        yield controller._refresh_access()

    assert account.access_token == expect.get('access_token')
    assert account.refresh_token == expect.get('refresh_token')
    assert (expect.get('token_expiration') - account.token_expiration) < (
        datetime.timedelta(seconds=10))


@pytest.mark.gen_test
def test_auth_controller_should_fetch_with_refresh(db, current_user):
    controller = CloudplayerController(db, current_user)
    account = controller.account
    account.token_expiration = datetime.datetime(2015, 7, 14, 12, 30)

    @tornado.gen.coroutine
    def fetch(path, method=None, **kw):
        response = mock.Mock()
        response.error = None
        if method:
            response.body = json.dumps({'access_token': 'access-token'})
        else:
            response.body = json.dumps({'path': path})
        return response

    with mock.patch.object(controller.http_client, 'fetch', fetch):
        response = yield controller.fetch('/path')

    fetched = tornado.escape.json_decode(response.body)
    assert fetched.get('path') == (
        'cp://base-api'
        '/path?token-param=access-token&client-key=cp-api-key')


@pytest.mark.gen_test
def test_auth_controller_should_fetch_anonymously(db):
    controller = CloudplayerController(db, {})

    @tornado.gen.coroutine
    def fetch(path, **kw):
        response = mock.Mock()
        response.error = None
        response.body = json.dumps({'path': path})
        return response

    with mock.patch.object(controller.http_client, 'fetch', fetch):
        response = yield controller.fetch('/path')

    fetched = tornado.escape.json_decode(response.body)
    assert fetched.get('path') == (
        'cp://base-api/path?client-key=cp-api-key')


def test_auth_controller_creates_account_from_info_dict(db):
    controller = CloudplayerController(db, {'user_id': '99'})
    controller._create_account({'id': 42})
    assert controller.account.id == '42'
    assert controller.account.user_id == '99'
    assert sqlalchemy.orm.util.object_state(controller.account).pending


def test_auth_controller_updates_access_info_to_account(db, current_user):
    controller = CloudplayerController(db, current_user)
    controller.account = account = Account()
    access_info = {
        'access_token': '1234',
        'refresh_token': '5678',
        'expires_in': 3600}
    controller._update_access_info(access_info)
    assert account.access_token == '1234'
    assert account.refresh_token == '5678'
    expiration = account.token_expiration - datetime.datetime.utcnow()
    assert datetime.timedelta(
        seconds=3590) < expiration < datetime.timedelta(seconds=3610)


def test_auth_controller_should_skip_updating_refresh_token(db, current_user):
    controller = CloudplayerController(db, current_user)
    controller.account = account = Account()
    access_info = {'access_token': '1234'}
    controller._update_access_info(access_info)
    assert account.access_token == '1234'
    assert account.refresh_token is None
    assert account.token_expiration is None


def test_auth_controller_syncs_cloudplayer_profile_from_account_info(
        db, current_user, account):
    # Check that account with unset attributes is synced
    account.title = None
    account.image = None

    controller = CloudplayerController(db, current_user)
    controller.account = Account(
        id='bar', title='foo', image=Image(large='image.co/large'),
        provider_id='soundcloud', user_id=current_user['user_id'])

    controller._sync_cloudplayer_profile()
    assert account.title == 'foo'
    assert account.image.small == controller.account.image.small
    assert account.image.medium == controller.account.image.medium
    assert account.image.large == controller.account.image.large

    # Check that account with set attributes is left alone
    controller.account = Account(title='bar', image=None)
    controller._sync_cloudplayer_profile()
    assert account.title == 'foo'
    assert account.image is not None


def test_auth_controller_updates_account_from_info_dicts(db, current_user):
    controller = CloudplayerController(db, current_user)
    access_info = {
        'access_token': 'xyz'}
    account_info = {
        'id': 1234,
        'title': 'foo bar',
        'image': Image(large='image.co/large')}
    controller.update_account(access_info, account_info)
    assert sqlalchemy.orm.util.object_state(controller.account).persistent
    assert controller.account.id == '1234'
    assert controller.account.title == 'foo bar'
    assert controller.account.image.large == 'image.co/large'
    assert controller.account.access_token == 'xyz'


def test_soundcloud_auth_updates_account_profile(db, current_user):
    controller = SoundcloudAuthController(db, current_user)
    account_info = {
        'id': 1234,
        'avatar_url': 'img.co/large.jpg',
        'username': 'foo bar'}
    controller._create_account(account_info)
    controller._update_account_profile(account_info)
    assert controller.account.id == '1234'
    assert controller.account.title == 'foo bar'
    assert controller.account.image.small == 'img.co/large.jpg'
    assert controller.account.image.medium == 'img.co/t300x300.jpg'
    assert controller.account.image.large == 'img.co/t500x500.jpg'


@pytest.mark.gen_test
def test_youtube_auth_inserst_additional_params_into_fetch(
        db, current_user, monkeypatch):
    fetch = mock.MagicMock()
    monkeypatch.setattr(
        AuthController, 'fetch', tornado.gen.coroutine((fetch)))
    controller = YoutubeAuthController(db, current_user)
    user_hash = hashlib.md5(current_user['cloudplayer'].encode()).hexdigest()

    yield controller.fetch('/path', [('p1', '1'), ('p2', '2')], kw0='kw0')

    fetch.assert_called_once_with(
        controller,
        '/path',
        params=[
            ('p1', '1'),
            ('p2', '2'),
            ('prettyPrint', 'false'),
            ('quotaUser', user_hash)],
        headers={'Referer': 'http://localhost'},
        kw0='kw0')


def test_youtube_auth_updates_account_profile(db, current_user):
    controller = YoutubeAuthController(db, current_user)
    account_info = {
        'id': 'xyz',
        'snippet': {
            'thumbnails': {
                'default': {'url': 'img.xy/default.jpg'},
                'medium': {'url': 'img.xy/medium.jpg'},
                'high': {'url': 'img.xy/high.jpg'}},
            'title': 'foo bar'}}
    controller._create_account(account_info)
    controller._update_account_profile(account_info)
    assert controller.account.id == 'xyz'
    assert controller.account.title == 'foo bar'
    assert controller.account.image.small == 'img.xy/default.jpg'
    assert controller.account.image.medium == 'img.xy/medium.jpg'
    assert controller.account.image.large == 'img.xy/high.jpg'


def test_youtube_auth_extracts_account_info_from_items(
        db, current_user, monkeypatch):
    controller = YoutubeAuthController(db, current_user)
    update_account = mock.MagicMock()
    account_info = mock.Mock()
    monkeypatch.setattr(AuthController, 'update_account', update_account)
    controller.update_account({}, {'items': [account_info], 'foo': 'bar'})
    update_account.assert_called_once_with({}, account_info)
