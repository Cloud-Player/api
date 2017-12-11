import pytest
import tornado.options as opt

import cloudplayer.api.app


@pytest.fixture(scope='session', autouse=True)
def app():
    opt.define('connect_timeout', default=3, group='httpclient')
    opt.define('request_timeout', default=3, group='httpclient')
    opt.define('max_redirects', default=1, group='httpclient')
    opt.define('google_oauth', default={'key': '', 'secret': ''}, group='app')
    opt.define('allowed_origins', default=['*'], group='app')
    return cloudplayer.api.app.make_app()
