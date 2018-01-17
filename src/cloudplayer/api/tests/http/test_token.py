import datetime
import json

from http.cookies import SimpleCookie
import jwt
import pytest
import tornado.escape

from cloudplayer.api.model.token import Token
from cloudplayer.api.model import Encoder


@pytest.mark.gen_test
def test_token_collection_should_create_new_token_anonymously(db, user_fetch):
    response = yield user_fetch('/token', method='POST', body='')
    token = tornado.escape.json_decode(response.body)
    assert len(token['id']) == 6
    assert token['claimed'] is False
    entity = db.query(Token).get(token['id'])
    assert entity.account is None
    assert entity.account_provider_id is None


@pytest.mark.gen_test
def test_token_entity_should_not_find_non_existent_entities(user_fetch):
    response = yield user_fetch('/token/not-an-id', raise_error=False)
    assert response.code == 404


@pytest.mark.gen_test
def test_token_entity_should_not_find_expired_entities(db, user_fetch):
    entity = Token()
    db.add(entity)
    db.commit()
    entity.created = entity.created - datetime.timedelta(minutes=100)
    db.commit()

    response = yield user_fetch(
        '/token/{}'.format(entity.id), raise_error=False)
    assert response.code == 404


@pytest.mark.gen_test
def test_token_entity_should_find_unclaimed_entites(
        http_client, base_url, db):
    entity = Token()
    db.add(entity)
    db.commit()

    response = yield http_client.fetch(
        '{}/token/{}'.format(base_url, entity.id))
    token = tornado.escape.json_decode(response.body)
    assert token['claimed'] is False
    assert tornado.escape.json_decode(response.body) == json.loads(
        json.dumps(entity, cls=Encoder))


@pytest.mark.gen_test
def test_token_entity_should_set_cookie_for_claimed_entites(
        db, http_client, current_user, base_url):
    entity = Token()
    entity.account_id = current_user['cloudplayer']
    entity.account_provider_id = 'cloudplayer'
    entity.claimed = True
    db.add(entity)
    db.commit()

    response = yield http_client.fetch(
        '{}/token/{}'.format(base_url, entity.id))
    token = tornado.escape.json_decode(response.body)
    assert token['claimed'] is True
    assert tornado.escape.json_decode(response.body) == json.loads(
        json.dumps(entity, cls=Encoder))
    cookie = SimpleCookie()
    cookie.load(response.headers['Set-Cookie'])
    assert jwt.decode(cookie.popitem()[1].value, verify=False) == current_user

    db.refresh(entity)
    assert entity.account_id is None
    assert entity.account_provider_id is None


@pytest.mark.gen_test
def test_token_entity_should_update_claimed_attribute(
        user_fetch, db, current_user):
    entity = Token()
    db.add(entity)
    db.commit()

    token = {'id': entity.id, 'claimed': True}
    response = yield user_fetch(
        '/token/{}'.format(entity.id), method='PATCH',
        body=json.dumps(token, cls=Encoder))

    db.refresh(entity)
    assert entity.claimed is True
    assert entity.account_id == current_user['cloudplayer']
    assert entity.account_provider_id == 'cloudplayer'


@pytest.mark.gen_test
def test_token_entity_should_always_set_claim_attribute_true(
        user_fetch, db, current_user):
    entity = Token()
    db.add(entity)
    db.commit()

    token = {'id': entity.id, 'claimed': False}
    response = yield user_fetch(
        '/token/{}'.format(entity.id), method='PATCH',
        body=json.dumps(token, cls=Encoder))

    db.refresh(entity)
    assert entity.claimed is True
