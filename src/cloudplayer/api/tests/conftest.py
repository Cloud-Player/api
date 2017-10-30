import pytest
import tornado.options as opt

import cloudplayer.api.app


@pytest.fixture(scope='session', autouse=True)
def app():
    opt.define('connect_timeout', type=int, default=3, group='httpclient')
    opt.define('request_timeout', type=int, default=3, group='httpclient')
    opt.define('max_redirects', type=int, default=1, group='httpclient')
    opt.define('allowed_origins', type=str, default='*')
    return cloudplayer.api.app.make_app()
