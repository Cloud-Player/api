import sys
import os.path
__path__ = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, __path__)

debug = True
xheaders = False
static_path = 'static'

providers = [
    'youtube',
    'soundcloud',
    'cloudplayer']

allowed_origins = [
    'http://localhost:8080',
    'http://0.0.0.0:8080',
    'http://127.0.0.1:8080']

jwt_secret = 'secret'

google_oauth = {
    'key': 'key',
    'secret': 'secret',
    'redirect_uri': 'http://localhost:8040/google'}

soundcloud_oauth = {
    'key': 'key',
    'secret': 'secret',
    'redirect_uri': 'http://localhost:8040/soundcloud'}

try:
    from private import *
except ImportError:
    pass
