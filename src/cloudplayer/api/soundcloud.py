import cloudplayer.api.handler


class LoginHandler(cloudplayer.api.handler.LoginHandler):

    _OAUTH_AUTHORIZE_URL = 'https://soundcloud.com/connect'
    _OAUTH_ACCESS_TOKEN_URL = 'https://api.soundcloud.com/oauth2/token'
    _OAUTH_USERINFO_URL = 'https://api.soundcloud.com/me'
    _OAUTH_SETTINGS_KEY = 'soundcloud_oauth'
    _OAUTH_PROVIDER_ID = 'soundcloud'
    _OAUTH_SCOPE_LIST = ['*']
    _OAUTH_EXTRA_PARAMS = {}
