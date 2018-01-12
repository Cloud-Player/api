import sqlalchemy as sql

from cloudplayer.api.model.account import Account
import cloudplayer.api.model.base as model


def test_account_model_should_create_table(db):
    account = sql.Table(
        'account', model.Base.metadata, autoload=True,
        autoload_with=db)
    assert account.exists(db.connection())


def test_account_model_can_be_created(current_user, db):
    account = Account(
        id='abcd1234',
        user_id=current_user['user_id'],
        provider_id='cloudplayer')
    db.add(account)
    db.commit()
    db.expunge(account)
    assert db.query(Account).get(('abcd1234', 'cloudplayer'))
