import requests
import logging
from time import sleep

# Local import
from .utils import get_backend_endpoint, get_jwt
from .utils.decorator import api_to_django_execute
from API.backend.exception import NoRetryError, RetryError
from API.backend.constants import WAITING_FOR_ERROR_API_SENDING, SEND_API_RETRY_COUNT_WHEN_STOP, API_SENDING_TIMEOUT


class TokenModuleBase:
    BASE_ENDPOINT = 'bio/token/{module_id}/'

    def __init__(self, backend_endpoint: str, bio_jwt: str, module_id: int):
        self.endpoint = f'{backend_endpoint}{self.BASE_ENDPOINT.format(module_id = module_id)}'
        self.headers = {'Authorization': f'Token {bio_jwt}'}
        self.module_id = module_id

    @api_to_django_execute
    def use(self, amount: int, timeout : int = API_SENDING_TIMEOUT):
        return requests.post(
            url=self.endpoint,
            data={
                'update_type': 'use',
                'used': amount
            },
            headers=self.headers,
            timeout=timeout,
        )

    @api_to_django_execute
    def set(self, amount: int, timeout : int = API_SENDING_TIMEOUT):
        return requests.post(
            url=self.endpoint,
            data={
                'update_type': 'set',
                'used': amount
            },
            headers=self.headers,
            timeout=timeout,
        )

    @api_to_django_execute
    def use_by_percent(self, percent: int, timeout : int = API_SENDING_TIMEOUT):
        return requests.post(
            url=self.endpoint,
            data={
                'update_type': 'use_by_percent',
                'used': percent
            },
            headers=self.headers,
            timeout=timeout,
        )

    def use_all_tokens(self):
        self.use_by_percent(100, timeout=10)

class TokenModule:
    def __init__(self, module_id: int):
        endpoint = get_backend_endpoint()
        jwt = get_jwt()
        self._token = TokenModuleBase(endpoint, jwt, module_id)

    def token(self) -> TokenModuleBase:
        return self._token

    def send_use_all(self, retry_count: int = SEND_API_RETRY_COUNT_WHEN_STOP):  # 120*5 = 10 minutes
        while retry_count > 0:
            try:
                self.token().use_all_tokens()
                retry_count = 0
                return True
            except RetryError as ex:
                logging.error(f'Token - {ex}')
                if retry_count > 0:
                    retry_count -= 1
                    sleep(WAITING_FOR_ERROR_API_SENDING)    # sleep 5 seconds
            except Exception as ex:
                retry_count = 0
                logging.error(f'Token - {ex}')
        return False