import sys
import os.path
__path__ = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, __path__)

debug = False
xheaders = True
static_path = 'static'

providers = [
    'youtube',
    'soundcloud',
    'cloudplayer']

allowed_origins = [
    'https://cloud-player.io',
    'http://localhost:8080',
    'http://0.0.0.0:8080',
    'http://127.0.0.1:8080']

jwt_secret = 'secret'

google_oauth = {
    'key': 'key',
    'secret': 'secret',
    'redirect_uri': 'https://api.cloud-player.io/google'}

soundcloud_oauth = {
    'key': 'key',
    'secret': 'secret',
    'redirect_uri': 'https://api.cloud-player.io/soundcloud'}

try:
    from private import *
except ImportError:
    pass
