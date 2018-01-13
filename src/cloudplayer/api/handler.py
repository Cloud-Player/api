"""
    cloudplayer.api.handler
    ~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
import datetime
import urllib

import jwt
import jwt.exceptions
import redis
import tornado.auth
import tornado.escape
import tornado.gen
import tornado.httputil
import tornado.options as opt
import tornado.web

from cloudplayer.api.model import Encoder
from cloudplayer.api.model.account import Account
from cloudplayer.api.model.user import User


class HandlerMixin(object):

    @property
    def cache(self):
        if not hasattr(self, '_cache'):
            self._cache = redis.Redis(
                connection_pool=self.application.redis_pool)
        return self._cache

    @property
    def http_client(self):
        if not hasattr(self, '_http_client'):
            self._http_client = tornado.httpclient.AsyncHTTPClient()
        return self._http_client

    @property
    def db(self):
        if not hasattr(self, '_db'):
            self._db = self.application.database.create_session()
        return self._db

    def finish(self, chunk=None):
        self.db.close()
        super().finish(chunk=chunk)

    def write_error(self, status_code, **kw):
        reason = 'no reason given'
        if 'reason' in kw:
            reason = kw['reason']
        elif 'exc_info' in kw:
            exception = kw['exc_info'][1]
            for attr in ('reason', 'message', 'log_message'):
                if getattr(exception, attr, None):
                    reason = getattr(exception, attr)
                    break
        self.set_status(status_code)
        self.write({'status_code': status_code, 'reason': reason})

    @tornado.gen.coroutine
    def fetch(self, provider_id, path, params=[], **kw):
        import cloudplayer.api.http.auth
        if provider_id == 'youtube':
            auth_class = cloudplayer.api.http.auth.Youtube
        elif provider_id == 'soundcloud':
            auth_class = cloudplayer.api.http.auth.Soundcloud
        else:
            raise ValueError('unsupported provider')
        url = '{}/{}'.format(auth_class.API_BASE_URL, path.lstrip('/'))
        settings = self.settings[auth_class._OAUTH_SETTINGS_KEY]

        account = self.db.query(Account).get((
            self.current_user[provider_id], provider_id))

        if account:
            # TODO: Move refresh workflow to auth module
            # TODO: Set quotaUser for Youtube
            tzinfo = account.token_expiration.tzinfo
            now = datetime.datetime.now(tzinfo)
            threshold = datetime.timedelta(minutes=1000000000)
            if account.token_expiration - now < threshold:
                body = urllib.parse.urlencode({
                    'client_id': settings['key'],
                    'client_secret': settings['secret'],
                    'refresh_token': account.refresh_token,
                    'grant_type': 'refresh_token'
                })
                uri = auth_class._OAUTH_ACCESS_TOKEN_URL
                response = yield self.http_client.fetch(
                    uri, method='POST', body=body, raise_error=False)
                access = tornado.escape.json_decode(response.body)
                account.access_token = access.get('access_token')
                if access.get('refresh_token'):
                    account.refresh_token = access['refresh_token']
                if access.get('expires_in'):
                    expires_in = datetime.timedelta(
                        seconds=access.get('expires_in'))
                    account.token_expiration = (
                        datetime.datetime.now(tzinfo) + expires_in)
                self.db.commit()
            params.append((auth_class.OAUTH_TOKEN_PARAM, account.access_token))

        params.append((auth_class._OAUTH_CLIENT_KEY, settings['api_key']))

        uri = tornado.httputil.url_concat(url, params)

        headers = kw.get('headers', {})
        headers['Referer'] = 'https://api.cloud-player.io'
        kw['headers'] = headers

        response = yield self.http_client.fetch(uri, **kw)
        return response


class ControllerHandlerMixin(object):

    __controller__ = NotImplemented

    @property
    def controller(self):
        if not hasattr(self, '_controller'):
            self._controller = self.__controller__(self.db, self.current_user)
        return self._controller


class EntityMixin(ControllerHandlerMixin):

    SUPPORTED_METHODS = ('GET', 'PATCH', 'DELETE')

    @tornado.gen.coroutine
    def get(self, **ids):
        entity = self.controller.read(ids)
        yield self.write(entity)

    @tornado.gen.coroutine
    def patch(self, **ids):
        entity = self.controller.update(ids, **self.body)
        yield self.write(entity)

    @tornado.gen.coroutine
    def delete(self, **ids):
        entity = self.controller.delete(ids)
        self.set_status(204)
        self.finish()


class CollectionMixin(ControllerHandlerMixin):

    SUPPORTED_METHODS = ('GET', 'POST')

    @tornado.gen.coroutine
    def get(self, **ids):
        query = dict(self.query_params)
        entities = self.controller.search(ids, **query)
        yield self.write(entities)

    @tornado.gen.coroutine
    def post(self, **ids):
        entity = self.controller.create(ids, **self.body)
        yield self.write(entity)
