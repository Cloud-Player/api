debug = True
xheaders = False
static_path = 'static'

allowed_origins = [
    'http://localhost:8080',
    'http://0.0.0.0:8080',
    'http://127.0.0.1:8080']

jwt_secret = 'secret'

google_oauth = {
    'key': 'key',
    'secret': 'secret',
    'redirect_uri': 'http://localhost:8040/google'}
