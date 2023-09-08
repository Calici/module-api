import requests
from API.backend.exception import NoRetryError, RetryError

def api_to_django_execute(org_func):
    """
    Using
    @api_execute
    def function_name(...)
    """
    def f_wrapper(*args, **kwargs):
        try:
            post_req = org_func(*args, **kwargs)
            if post_req.status_code == 200:
                return post_req
            elif post_req.status_code == 502:
                # Timeout connecting from nginx to django
                raise RetryError(post_req)
            else: 
                raise NoRetryError(post_req)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as ex:
            raise RetryError('Connection error or timeout occurred')
    return f_wrapper