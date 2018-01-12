import sqlalchemy as sql

from cloudplayer.api.model.playlist import Playlist
import cloudplayer.api.model.base as model


def test_playlist_model_should_create_table(db):
    playlist = sql.Table(
        'playlist', model.Base.metadata, autoload=True,
        autoload_with=db)
    assert playlist.exists(db.connection())


def test_playlist_model_can_be_created(current_user, db):
    playlist = Playlist(
        provider_id='cloudplayer',
        account_id=current_user['cloudplayer'],
        title='5678-abcd')
    db.add(playlist)
    db.commit()
    playlist_id = playlist.id
    db.expunge(playlist)
    assert db.query(Playlist).get((playlist_id, 'cloudplayer'))
