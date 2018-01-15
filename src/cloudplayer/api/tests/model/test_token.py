import sqlalchemy as sql

from cloudplayer.api.model.token import Token
import cloudplayer.api.model.base as model


def test_token_model_should_create_table(db):
    token = sql.Table(
        'token', model.Base.metadata, autoload=True,
        autoload_with=db)
    assert token.exists(db.connection())


def test_token_model_can_be_created(current_user, db):
    token = Token(
        account_id=current_user['cloudplayer'],
        account_provider_id='cloudplayer')
    db.add(token)
    db.commit()
    token_id = token.id
    db.expunge(token)
    assert db.query(Token).get(token_id)
