import os
import sys
import random

import sqlalchemy as sql
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
    opt.define('youtube', group='app', default={
        'key': 'yt-key', 'secret': 'yt-secret', 'api_key': 'yt-api-key'})
    opt.define('cloudplayer', group='app', default={
        'key': 'cp-key', 'secret': 'cp-secret', 'api_key': 'cp-api-key'})
    opt.define('soundcloud', group='app', default={
        'key': 'sc-key', 'secret': 'sc-secret', 'api_key': 'sc-api-key'})
    opt.define('jwt_cookie', default='tok_v1', group='app')
    opt.define('jwt_expiration', default=1, group='app')
    opt.define('jwt_secret', default='secret', group='app')
    opt.define('providers', default=[
        'youtube', 'soundcloud', 'cloudplayer'], group='app')
    opt.define('allowed_origins', default=['*'], group='app')
    opt.define('num_executors', default=1, group='app')
    opt.define('menuflow_state', default='dev', group='app')
    opt.define('redis_host', default=redis_proc.host, group='app')
    opt.define('redis_port', default=redis_proc.port, group='app')
    opt.define('redis_db', default=0, group='app')
    opt.define('redis_password', default=None, group='app')
    opt.define('postgres_host', default=postgresql_proc.host, group='app')
    opt.define('postgres_port', default=postgresql_proc.port, group='app')
    opt.define('postgres_db', default='postgres', group='app')
    opt.define('postgres_user', default='postgres', group='app')
    opt.define('postgres_password', default='', group='app')
    app = cloudplayer.api.app.Application()
    yield app
    app.database.engine.dispose()


@pytest.fixture(scope='function')
def db(app):
    import cloudplayer.api.model.base as model
    app.database.initialize()
    session = app.database.create_session()
    yield session
    for table in reversed(model.Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
    session.close()


@pytest.fixture(scope='function')
def current_user(db):
    from cloudplayer.api.model.user import User
    from cloudplayer.api.model.account import Account
    user = User()
    db.add(user)
    db.commit()
    account = Account(
        id=str(user.id),
        provider_id='cloudplayer',
        user_id=user.id)
    db.add(account)
    db.commit()
    return {'user_id': user.id, 'cloudplayer': account.id}
