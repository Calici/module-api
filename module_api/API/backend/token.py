import requests
import logging
from time import sleep

# Local import
from .utils import get_backend_endpoint, get_jwt
from .utils.decorator import backend_api_call
from module_api.API.backend.constants import \
    WAITING_FOR_ERROR_API_SENDING, \
    SEND_API_RETRY_COUNT_WHEN_STOP, \
    API_SENDING_TIMEOUT

class TokenAPI:
    def __init__(self, module_id : int):
        self.endpoint = '{0}bio/token/{1}/'.format(
            get_backend_endpoint(), module_id
        )
        self.headers = {
            'Authorization' : 'Token {0}'.format(get_jwt())
        }
        self.module_id = module_id
    @backend_api_call()
    def use(self, amount : int, timeout : int = API_SENDING_TIMEOUT):
        return requests.post(
            url = self.endpoint, 
            data = { 'update_type' : 'use', 'used' : amount }, 
            headers = self.headers, 
            timeout = timeout
        )
    @backend_api_call()
    def set(self, amount : int, timeout : int = API_SENDING_TIMEOUT):
        return requests.post(
            url = self.endpoint, 
            data = { 'update_type' : 'set', 'used' : amount }, 
            headers = self.headers, 
            timeout = timeout
        )
    @backend_api_call()
    def use_percent(self, percent : int, timeout : int = API_SENDING_TIMEOUT):
        return requests.post(
            url = self.endpoint, 
            data = {'update_type' : 'use_by_percent', 'used' : percent},
            headers = self.headers,
            timeout = timeout
        )
    def use_all_tokens(self, timeout : int = 10):
        self.use_percent(100, timeout)

