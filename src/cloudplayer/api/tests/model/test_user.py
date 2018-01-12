import sqlalchemy as sql

from cloudplayer.api.model.user import User
import cloudplayer.api.model.base as model


def test_user_model_should_create_table(db):
    user = sql.Table(
        'user', model.Base.metadata, autoload=True,
        autoload_with=db)
    assert user.exists(db.connection())


def test_user_model_can_be_created(db):
    user = User()
    db.add(user)
    db.commit()
    user_id = user.id
    db.expunge(user)
    assert db.query(User).get(user_id)
