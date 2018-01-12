import sqlalchemy as sql
import cloudplayer.api.model.base as model


def test_token_model_should_create_table(db):
    token = sql.Table(
        'token', model.Base.metadata, autoload=True,
        autoload_with=db)
    assert token.exists(db.connection())
