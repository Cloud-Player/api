import sqlalchemy as sql
import cloudplayer.api.model.base as model


def test_account_model_should_create_table(db):
    account = sql.Table(
        'account', model.Base.metadata, autoload=True,
        autoload_with=db)
    assert account.exists(db.connection())
