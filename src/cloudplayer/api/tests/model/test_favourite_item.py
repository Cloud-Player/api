import sqlalchemy as sql

from cloudplayer.api.model.favourite import Favourite
from cloudplayer.api.model.favourite_item import FavouriteItem
import cloudplayer.api.model.base as model


def test_favourite_item_model_should_create_table(db):
    favourite_item = sql.Table(
        'favouriteitem', model.Base.metadata, autoload=True,
        autoload_with=db)
    assert favourite_item.exists(db.connection())


def test_favourite_item_model_can_be_created(current_user, db):
    favourite_item = FavouriteItem(
        favourite_provider_id='cloudplayer',
        favourite=Favourite(
            provider_id='cloudplayer',
            account_id=current_user['cloudplayer'],
            account_provider_id='cloudplayer'),
        account_provider_id='cloudplayer',
        account_id=current_user['cloudplayer'],
        track_provider_id='cloudplayer',
        track_id='abcd-1234')
    db.add(favourite_item)
    db.commit()
    favourite_item_id = favourite_item.id
    db.expunge_all()
    assert db.query(FavouriteItem).get(favourite_item_id)
