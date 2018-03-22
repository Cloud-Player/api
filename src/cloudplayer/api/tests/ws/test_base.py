import pytest


@pytest.mark.gen_test
def test_websocket_connection_responds_with_fallback(user_push):
    not_found = yield user_push({'channel': 'cannot.be.found'})
    assert not_found == {
        'channel': 'cannot.be.found',
        'sequence': 0,
        'body': {
            'reason': 'channel not found',
            'status_code': 404}}
