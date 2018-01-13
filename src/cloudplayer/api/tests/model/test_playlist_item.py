import sqlalchemy as sql

from cloudplayer.api.model.playlist import Playlist
from cloudplayer.api.model.playlist_item import PlaylistItem
import cloudplayer.api.model.base as model


def test_playlist_item_model_should_create_table(db):
    playlist_item = sql.Table(
        'playlistitem', model.Base.metadata, autoload=True,
        autoload_with=db)
    assert playlist_item.exists(db.connection())


def test_playlist_item_model_can_be_created(current_user, db):
    playlist_item = PlaylistItem(
        rank='aaa',
        playlist_provider_id='cloudplayer',
        playlist=Playlist(
            provider_id='cloudplayer',
            account_id=current_user['cloudplayer'],
            title='5678-abcd'),
        account_provider_id='cloudplayer',
        account_id=current_user['cloudplayer'],
        track_provider_id='cloudplayer',
        track_id='abcd-1234')
    db.add(playlist_item)
    db.commit()
    playlist_item_id = playlist_item.id
    db.expunge_all()
    assert db.query(PlaylistItem).get(playlist_item_id)
