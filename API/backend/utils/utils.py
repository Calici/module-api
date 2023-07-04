import random
import string

def random_string(length : int) -> str:
    return ''.join([random.choice(string.ascii_letters) for i in range(length)])

def get_jwt() -> str:
    from flask_backend.backend.main.config import JWT_SECRET
    from flask_backend.backend.utils.jwt import JWT
    from .utils import random_string
    header  = {'typ' : 'jwt', 'alg' : 'sha256'}
    payload = {'cmp' : random_string(16), 'mpc' : random_string(16), 'pcm' : random_string(16)}
    jwt     = JWT(header = header, payload = payload, secret = JWT_SECRET['BIO'])
    return jwt.encode()

def get_backend_endpoint() -> str:
    from flask_backend.backend.main.config import DJANGO_BACKEND_URL
    return DJANGO_BACKEND_URL