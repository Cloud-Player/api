import sqlalchemy as sql

from cloudplayer.api.model.provider import Provider
import cloudplayer.api.model.base as model


def test_provider_model_should_create_table(db):
    provider = sql.Table(
        'provider', model.Base.metadata, autoload=True,
        autoload_with=db)
    assert provider.exists(db.connection())


def test_provider_model_can_be_created(db):
    provider = Provider(
        id='abcd')
    db.add(provider)
    db.commit()
    db.expunge(provider)
    assert db.query(Provider).get('abcd')
