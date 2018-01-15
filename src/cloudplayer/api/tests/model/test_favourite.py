import sqlalchemy as sql

from cloudplayer.api.model.favourite import Favourite
import cloudplayer.api.model.base as model


def test_favourite_model_should_create_table(db):
    favourite = sql.Table(
        'favourite', model.Base.metadata, autoload=True,
        autoload_with=db)
    assert favourite.exists(db.connection())


def test_favourite_model_can_be_created(current_user, db):
    favourite = Favourite(
        provider_id='cloudplayer',
        account_id=current_user['cloudplayer'],
        account_provider_id='cloudplayer')
    db.add(favourite)
    db.commit()
    favourite_id = favourite.id
    db.expunge(favourite)
    assert db.query(Favourite).get((favourite_id, 'cloudplayer'))
