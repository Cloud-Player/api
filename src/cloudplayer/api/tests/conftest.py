import pytest
import tornado.options as opt

import cloudplayer.api.app


@pytest.fixture(scope='session', autouse=True)
def app():
    opt.define('connect_timeout', default=3, group='httpclient')
    opt.define('request_timeout', default=3, group='httpclient')
    opt.define('max_redirects', default=1, group='httpclient')
    opt.define('google_oauth', default={
        'key': 'g-auth', 'secret': 'g-secret'}, group='app')
    opt.define('soundcloud_oauth', default={
        'key': 'sc-auth', 'secret': 'sc-secret'}, group='app')
    opt.define('jwt_secret', default='secret', group='app')
    opt.define('allowed_origins', default=['*'], group='app')
    opt.define('num_executors', type=int, default=1, group='app')
    opt.define('redis_host', type=str, default='localhost', group='app')
    opt.define('redis_port', type=int, default=6379, group='app')
    opt.define('postgres_host', type=str, default='localhost', group='app')
    opt.define('postgres_port', type=int, default=5432, group='app')
    opt.define('postgres_db', type=str, default='cloudplayer', group='app')
    opt.define('postgres_user', type=str, default='api', group='app')
    opt.define('postgres_password', type=str, default='password', group='app')
    return cloudplayer.api.app.Application()
