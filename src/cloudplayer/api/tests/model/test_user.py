import sqlalchemy as sql
import cloudplayer.api.model.base as model


def test_user_model_should_create_table(db):
    user = sql.Table(
        'user', model.Base.metadata, autoload=True,
        autoload_with=db)
    assert user.exists(db.connection())
