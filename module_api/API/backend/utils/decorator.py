import requests
from module_api.API.backend.exception import \
    NoRetryError, \
    RetryError, \
    APICallError
from module_api.API.backend.constants import \
    WAITING_FOR_ERROR_API_SENDING
from requests.exceptions import \
    Timeout, \
    ConnectionError
from typing_extensions import \
    Callable, \
    ParamSpec
import time

P = ParamSpec('P')
def run_query(
    func : Callable[P, requests.Response], *args : P.args, **kwargs : P.kwargs
) -> requests.Response:
    """
        Perform the query func with the given parameters *args, **kwargs
    """
    try:
        response = func(*args, **kwargs)
        if response.status_code == 200:
            return response
        elif response.status_code == 502:
            # Backend Restarting Error (NGINX)
            raise RetryError(response)
        else:
            raise NoRetryError(response)
    except (ConnectionError, Timeout):
        raise RetryError("Connection error or timeout occurred")

def backend_api_call(
    retry_count : int = 5, 
    retry_interval : float = WAITING_FOR_ERROR_API_SENDING
) -> Callable[
    [Callable[..., requests.Response]], Callable[..., requests.Response]
]:
    """
        Usage : 
        @backend_api_call(retry_count = 5, retry_interval = ...)
        def api_call_function( ... ) -> requests.Response
            ...
        This decorator schedules resend of requests for failed requests.
        Retries the request for retry_count times with retry_interval time.
    """
    def decorator(func : Callable[..., requests.Response]):
        def decorated_function(*args, **kwargs):
            for _ in range(retry_count):
                try:
                    return run_query(func, *args, **kwargs)
                except RetryError:
                    pass
                except NoRetryError:
                    break
                time.sleep(retry_interval)
            raise APICallError('API Call have failed')
        return decorated_function
    return decorator