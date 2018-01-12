import sqlalchemy as sql
import cloudplayer.api.model.base as model


def test_playlist_model_should_create_table(db):
    playlist = sql.Table(
        'playlist', model.Base.metadata, autoload=True,
        autoload_with=db)
    assert playlist.exists(db.connection())
