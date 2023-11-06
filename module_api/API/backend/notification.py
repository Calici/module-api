import requests
from .utils import get_backend_endpoint, get_jwt
from .utils.decorator import backend_api_call
from module_api.API.backend.constants import API_SENDING_TIMEOUT
from typing_extensions import \
    Literal, \
    Union

class NotificationStatus:
    COMPLETE = 'COMPLETE'
    ERROR = 'ERROR'
    GENERAL = 'GENERAL'
    WARNING = 'WARNING'
    Type = Union[
        Literal['COMPLETE'], 
        Literal['ERROR'], 
        Literal['GENERAL'], 
        Literal['WARNING']
    ]

class NotificationAPI:
    def __init__(self, module_id : int):
        self.endpoint = ' {0}bio/notification/'.format(get_backend_endpoint())
        self.headers = { 'Authorization' : 'Token {0}'.format(get_jwt()) }
        self.module_id = module_id
    
    @backend_api_call(retry_count = 5)
    def create(self, 
        title : str,
        content : str, 
        type : NotificationStatus.Type = NotificationStatus.GENERAL, 
        timeout : int = API_SENDING_TIMEOUT
    ) -> requests.Response:
        return requests.post(
            url = self.endpoint,
            data = {
                'title' : title,
                'content' : content, 
                'type' : type, 
                'module' : self.module_id
            }, 
            timeout = timeout
        )
    