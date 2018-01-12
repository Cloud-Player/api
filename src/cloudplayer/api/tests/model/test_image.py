import sqlalchemy as sql

from cloudplayer.api.model.image import Image
import cloudplayer.api.model.base as model


def test_image_model_should_create_table(db):
    image = sql.Table(
        'image', model.Base.metadata, autoload=True,
        autoload_with=db)
    assert image.exists(db.connection())


def test_image_model_can_be_created(db):
    image = Image(
        large='http://img.host/large.jpg')
    db.add(image)
    db.commit()
    image_id = image.id
    db.expunge(image)
    assert db.query(Image).get(image_id)
