import datetime

import pytest

from cloudplayer.api.access import PolicyViolation
from cloudplayer.api.controller import ControllerException
from cloudplayer.api.controller.token import TokenController
from cloudplayer.api.model.account import Account
from cloudplayer.api.model.token import Token
from cloudplayer.api.model.user import User


@pytest.mark.gen_test
async def test_controller_should_create_new_token_anonymously(
        db, current_user):
    controller = TokenController(db, current_user)
    token = await controller.create({}, {})
    assert token.id is not None
    assert token.account_id is None
    assert token.account_provider_id is None
    assert token.claimed is False


@pytest.mark.gen_test
async def test_controller_should_not_create_token_with_kw(db, current_user):
    controller = TokenController(db, current_user)
    with pytest.raises(PolicyViolation):
        await controller.create({}, {'account_id': '1234'})


@pytest.mark.gen_test
async def test_controller_should_not_find_non_existent_entities(
        db, current_user):
    controller = TokenController(db, current_user)
    with pytest.raises(ControllerException):
        await controller.read({'id': 'not-an-id'})


@pytest.mark.gen_test
async def test_controller_should_not_find_expired_entities(db, current_user):
    entity = Token()
    db.add(entity)
    db.commit()
    entity.created = entity.created - datetime.timedelta(minutes=100)
    db.commit()
    controller = TokenController(db, current_user)
    with pytest.raises(ControllerException):
        await controller.read({'id': entity.id})


@pytest.mark.gen_test
async def test_controller_should_find_unclaimed_entites(db, current_user):
    entity = Token()
    db.add(entity)
    db.commit()
    controller = TokenController(db, current_user)
    token = await controller.read({'id': entity.id})
    assert token.claimed is False
    assert token.id == entity.id


@pytest.mark.gen_test
async def test_controller_should_set_current_user_on_claimed_token(
        db, current_user):
    entity = Token()
    account = Account(
        id='1234', user=User(), provider_id='cloudplayer')
    entity.account = account
    entity.claimed = True
    db.add_all((entity, entity.account, entity.account.user))
    db.commit()

    assert entity.account.id != current_user['cloudplayer']

    controller = TokenController(db, current_user)
    token = await controller.read({'id': entity.id})
    assert token.claimed is True
    assert token.id == entity.id
    assert account.user.id == current_user['user_id']

    db.refresh(entity)
    assert entity.account_id is None
    assert entity.account_provider_id is None


@pytest.mark.gen_test
async def test_token_entity_should_update_claimed_attribute(db, current_user):
    entity = Token()
    db.add(entity)
    db.commit()

    token = {
        'id': entity.id,
        'claimed': True,
        'account_id': current_user['cloudplayer'],
        'account_provider_id': 'cloudplayer'}
    controller = TokenController(db, current_user)
    await controller.update({'id': entity.id}, token)

    db.refresh(entity)
    assert entity.claimed is True
    assert entity.account_id == current_user['cloudplayer']
    assert entity.account_provider_id == 'cloudplayer'


@pytest.mark.gen_test
async def test_controller_should_expect_full_update_not_patch(
        db, current_user):
    entity = Token()
    db.add(entity)
    db.commit()

    token = {'id': entity.id, 'claimed': True}
    controller = TokenController(db, current_user)
    with pytest.raises(ControllerException):
        await controller.update({'id': entity.id}, token)
