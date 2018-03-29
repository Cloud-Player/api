import pytest


@pytest.mark.gen_test
def test_account_session_can_be_created_with_fingerprint(
        user_fetch, account, db):
    assert not account.sessions
    body = {'system': 'windows', 'browser': 'safari', 'screen': '1024x800'}
    response = yield user_fetch('/session', method='POST', body=body)
    assert response.json() == {}
    db.refresh(account)
    assert account.sessions
    session = account.sessions[0]
    assert session.system == 'windows'
    assert session.browser == 'safari'
    assert session.screen == '1024x800'
