import cloudplayer.api.util


def test_token_generator_should_create_token():
    token = cloudplayer.api.util.gen_token(10, 'abc')
    assert len(token) == 10
    assert all([t in 'abc' for t in token])
