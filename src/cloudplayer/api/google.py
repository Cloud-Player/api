import cloudplayer.api.handler


class LoginHandler(cloudplayer.api.handler.LoginHandler):

    _OAUTH_AUTHORIZE_URL = 'https://accounts.google.com/o/oauth2/auth'
    _OAUTH_ACCESS_TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
    _OAUTH_USERINFO_URL = 'https://www.googleapis.com/oauth2/v1/userinfo'
    _OAUTH_SETTINGS_KEY = 'google_oauth'
    _OAUTH_PROVIDER_ID = 'google'
    _OAUTH_SCOPE_LIST = [
        'profile', 'email', 'https://www.googleapis.com/auth/youtube']
    _OAUTH_EXTRA_PARAMS = {
        'approval_prompt': 'auto', 'access_type': 'offline'}
