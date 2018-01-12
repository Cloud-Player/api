import sqlalchemy as sql
import cloudplayer.api.model.base as model


def test_provider_model_should_create_table(db):
    provider = sql.Table(
        'provider', model.Base.metadata, autoload=True,
        autoload_with=db)
    assert provider.exists(db.connection())
