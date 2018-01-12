import sqlalchemy as sql
import cloudplayer.api.model.base as model


def test_playlist_item_model_should_create_table(db):
    playlist_item = sql.Table(
        'playlist_item', model.Base.metadata, autoload=True,
        autoload_with=db)
    assert playlist_item.exists(db.connection())
