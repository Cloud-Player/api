import sqlalchemy as sql
import cloudplayer.api.model.base as model


def test_image_model_should_create_table(db):
    image = sql.Table(
        'image', model.Base.metadata, autoload=True,
        autoload_with=db)
    assert image.exists(db.connection())
