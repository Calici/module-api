import random
import string
import os

def random_string(length : int) -> str:
    return ''.join([random.choice(string.ascii_letters) for i in range(length)])

def get_jwt() -> str:
    token = os.environ.get('DJANGO_API_TOKEN') 
    if token is None:
        raise RuntimeError("DJANGO_API_TOKEN has not been set")
    return token

def get_backend_endpoint() -> str:
    """
        Returns the backend endpoint guaranteeing a slash in the of the URL
    """
    endpoint = os.environ.get('DJANGO_API_ENDPOINT')
    if endpoint is None:
        raise RuntimeError("DJANGO_API_ENDPOINT has not been set")
    return endpoint if endpoint[-1] == '/' else endpoint + '/'
