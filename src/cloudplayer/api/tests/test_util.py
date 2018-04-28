from cloudplayer.api.util import gen_token, chunk_range, squeeze


def test_token_generator_should_create_token():
    token = gen_token(10, 'abc')
    assert len(token) == 10
    assert all([t in 'abc' for t in token])


def test_chunk_range_should_range_and_split_numbers():
    assert chunk_range(0, 0) == [(0, None)]
    assert chunk_range(3, 0) == [(0, None)]
    assert chunk_range(3, 1) == [(0, None)]
    assert chunk_range(3, 2) == [(0, 2), (2, None)]
    assert chunk_range(3, 3) == [(0, 1), (1, 2), (2, None)]
    assert chunk_range(3, 4) == [(0, 1), (1, 2), (2, None)]


def test_squeeze_should_reduce_string_to_non_whitespace_chars():
    assert squeeze('') == ''
    assert squeeze('hello') == 'hello'
    assert squeeze('good bye') == 'goodbye'
    assert squeeze("""
    multiple
    lines
    and words .
    """) == 'multiplelinesandwords.'
