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
    'http://localhost:4200',
    'http://localhost:8080']

jwt_secret = 'secret'

youtube_oauth = {
    'key': 'key',
    'secret': 'secret',
    'redirect_uri': 'http://localhost:8040/youtube'}

soundcloud_oauth = {
    'key': 'key',
    'secret': 'secret',
    'redirect_uri': 'http://localhost:8040/soundcloud'}

try:
    from private import *
except ImportError:
    pass
