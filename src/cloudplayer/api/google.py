import datetime

import tornado.gen
import tornado.auth

from cloudplayer.api.model import Account, User, Provider
import cloudplayer.api.handler


class LoginHandler(cloudplayer.api.handler.HTTPHandler,
                   tornado.auth.GoogleOAuth2Mixin):

    @tornado.gen.coroutine
    def get(self):
        if self.get_argument('code', False):
            access = yield self.get_authenticated_user(
                redirect_uri=self.settings['google_oauth']['redirect_uri'],
                code=self.get_argument('code'))
            user_info = yield self.oauth2_request(
                'https://www.googleapis.com/oauth2/v1/userinfo',
                access_token=access['access_token'])

            account = self.db.query(
                Account
            ).filter(
                Account.id == user_info['id']
            ).filter(
                Account.provider == 'youtube'
            ).one_or_none()

            if not account:
                account = Account(
                    id=user_info['id'],
                    provider='youtube',
                    title=user_info['name'],
                    image=user_info['picture'],
                    access_token=access['access_token'],
                    refresh_token=access['refresh_token'],
                    token_expiration=datetime.timedelta(
                        seconds=access['expires_in']))
                self.db.add(account)
                self.current_user.accounts.append(account)

            self.db.commit()
        else:
            yield self.authorize_redirect(
                redirect_uri=self.settings['google_oauth']['redirect_uri'],
                client_id=self.settings['google_oauth']['key'],
                scope=['profile', 'email',
                       'https://www.googleapis.com/auth/youtube'],
                response_type='code',
                extra_params={
                    'approval_prompt': 'auto',
                    'access_type': 'offline'})
