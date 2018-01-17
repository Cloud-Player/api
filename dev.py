import sys
import os.path
__path__ = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, __path__)

debug = True
xheaders = False
static_path = 'static'
menuflow_state = 'dev'

providers = [
    'youtube',
    'soundcloud',
    'cloudplayer']

allowed_origins = [
    'http://localhost:4200',
    'http://localhost:8040',
    'http://localhost:8080']

jwt_secret = 'secret'

youtube = {
    'key': 'key',
    'api_key': 'api_key',
    'secret': 'secret',
    'redirect_uri': 'http://localhost:8040/youtube'}

soundcloud = {
    'key': 'key',
    'api_key': 'api_key',
    'secret': 'secret',
    'redirect_uri': 'http://localhost:8040/soundcloud'}

cloudplayer = {
    'key': 'key',
    'api_key': 'api_key',
    'secret': 'secret',
    'redirect_uri': 'http://localhost:8040/cloudplayer'}

bugsnag = {
    'api_key': 'api_key',
    'project_root': '/usr/local/cloudplayer'
}

try:
    from private import *
except ImportError:
    pass
