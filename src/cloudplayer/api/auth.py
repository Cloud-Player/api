"""
    cloudplayer.api.auth
    ~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2017 by the cloudplayer team
    :license: GPL-3.0, see LICENSE for details
"""
import cloudplayer.api.handler


class Soundcloud(cloudplayer.api.handler.AuthHandler):

    API_BASE_URL = 'https://api.soundcloud.com'
    OAUTH_TOKEN_PARAM = 'oauth_token'

    _OAUTH_AUTHORIZE_URL = 'https://soundcloud.com/connect'
    _OAUTH_ACCESS_TOKEN_URL = 'https://api.soundcloud.com/oauth2/token'
    _OAUTH_USERINFO_URL = 'https://api.soundcloud.com/me'
    _OAUTH_SETTINGS_KEY = 'soundcloud_oauth'
    _OAUTH_PROVIDER_ID = 'soundcloud'
    _OAUTH_SCOPE_LIST = []
    _OAUTH_EXTRA_PARAMS = {'state': 'v3'}


class Youtube(cloudplayer.api.handler.AuthHandler):

    API_BASE_URL = 'https://www.googleapis.com/youtube/v3'
    OAUTH_TOKEN_PARAM = 'access_token'

    _OAUTH_AUTHORIZE_URL = 'https://accounts.google.com/o/oauth2/auth'
    _OAUTH_ACCESS_TOKEN_URL = 'https://www.googleapis.com/oauth2/v4/token'
    _OAUTH_USERINFO_URL = 'https://www.googleapis.com/oauth2/v1/userinfo'
    _OAUTH_SETTINGS_KEY = 'youtube_oauth'
    _OAUTH_PROVIDER_ID = 'youtube'
    _OAUTH_SCOPE_LIST = [
        'profile', 'email', 'https://www.googleapis.com/auth/youtube']
    _OAUTH_EXTRA_PARAMS = {
        'approval_prompt': 'auto', 'access_type': 'offline'}
