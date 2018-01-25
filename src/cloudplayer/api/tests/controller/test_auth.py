import datetime

import mock
import pytest

from cloudplayer.api.model.account import Account
from cloudplayer.api.controller.auth import (
    create_controller, AuthController,
    SoundcloudAuthController, YoutubeAuthController)


@pytest.mark.parametrize('id_, class_', [
    ('soundcloud', SoundcloudAuthController),
    ('youtube', YoutubeAuthController)])
def test_create_controller_should_return_correct_controller(id_, class_):
    controller = create_controller(id_, mock.Mock())
    assert isinstance(controller, class_)


def test_create_controller_should_reject_invalid_provider_id():
    with pytest.raises(ValueError):
        create_controller('not-a-provider', mock.Mock())


class CloudplayerController(AuthController):
    PROVIDER_ID = 'cloudplayer'


def test_auth_controller_should_provide_instance_args(db, current_user):
    controller = CloudplayerController(db, current_user)
    assert controller.db is db
    assert controller.current_user == current_user
    assert controller.settings == {
        'api_key': 'cp-api-key', 'key': 'cp-key', 'secret': 'cp-secret'}
    assert controller.account.id == current_user['cloudplayer']


def test_auth_controller_should_check_token_expiration_before_refresh(
        db, current_user):
    controller = CloudplayerController(db, current_user)
    a_second_ago = datetime.datetime.utcnow() - datetime.timedelta(seconds=1)
    controller.account.token_expiration = a_second_ago
    assert controller.should_refresh is True
    in_an_hour = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    controller.account.token_expiration = in_an_hour
    assert controller.should_refresh is False
    db.rollback()
