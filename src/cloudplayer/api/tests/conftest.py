import os
import sys

import pytest_redis.factories as redis_factories
import pytest
import tornado.options as opt

import cloudplayer.api.app


def which(executable):
    path = os.environ['PATH']
    paths = path.split(os.pathsep)
    extlist = ['']
    if os.name == 'os2':
        (base, ext) = os.path.splitext(executable)
        if not ext:
            executable = executable + '.exe'
    elif sys.platform == 'win32':
        pathext = os.environ['PATHEXT'].lower().split(os.pathsep)
        (base, ext) = os.path.splitext(executable)
        if ext.lower() not in pathext:
            extlist = pathext
    for ext in extlist:
        execname = executable + ext
        if os.path.isfile(execname):
            return execname
        else:
            for p in paths:
                f = os.path.join(p, execname)
                if os.path.isfile(f):
                    return f
    else:
        return None


redis_proc = redis_factories.redis_proc(executable=which('redis-server'))


@pytest.fixture(scope='session', autouse=True)
def app(postgresql_proc, redis_proc):
    opt.define('connect_timeout', default=3, group='httpclient')
    opt.define('request_timeout', default=3, group='httpclient')
    opt.define('max_redirects', default=1, group='httpclient')
    opt.define('youtube_oauth', default={
        'key': 'g-auth', 'secret': 'g-secret'}, group='app')
    opt.define('soundcloud_oauth', default={
        'key': 'sc-auth', 'secret': 'sc-secret'}, group='app')
    opt.define('jwt_cookie', default='tok_v1', group='app')
    opt.define('jwt_expiration', default=1, group='app')
    opt.define('jwt_secret', default='secret', group='app')
    opt.define('providers', default=[
        'youtube', 'soundcloud', 'cloudplayer'], group='app')
    opt.define('allowed_origins', default=['*'], group='app')
    opt.define('num_executors', type=int, default=1, group='app')
    opt.define('menuflow_state', type=str, default='dev', group='app')
    opt.define('redis_host', type=str, default='localhost', group='app')
    opt.define('redis_port', type=int, default=8869, group='app')
    opt.define('postgres_host', type=str, default='localhost', group='app')
    opt.define('postgres_port', type=int, default=8852, group='app')
    opt.define('postgres_db', type=str, default='postgres', group='app')
    opt.define('postgres_user', type=str, default='postgres', group='app')
    opt.define('postgres_password', type=str, default='', group='app')
    return cloudplayer.api.app.Application()
