import sys
import os.path
__path__ = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, __path__)

debug = False
xheaders = True
static_path = '/srv/cloudplayer/static'
redirect_state = 'v3'

providers = [
    'youtube',
    'soundcloud',
    'cloudplayer']

allowed_origins = [
    'https://cloud-player.io',
    'http://localhost:8080',
    'http://localhost:4200']

jwt_secret = 'secret'

youtube = {
    'key': 'key',
    'api_key': 'api_key',
    'secret': 'secret',
    'redirect_uri': 'https://api.cloud-player.io/youtube'}

soundcloud = {
    'key': 'key',
    'api_key': 'api_key',
    'secret': 'secret',
    'redirect_uri': 'https://api.cloud-player.io/soundcloud'}

cloudplayer = {
    'key': 'key',
    'api_key': 'api_key',
    'secret': 'secret',
    'redirect_uri': 'https://api.cloud-player.io/cloudplayer'}

bugsnag = {
    'api_key': 'api_key',
    'project_root': '/usr/local/cloudplayer'
}

try:
    from private import *
except ImportError:
    pass
