import requests
from .utils import get_backend_endpoint, get_jwt
from .utils.decorator import api_to_django_execute
from module_api.API.backend.constants import module_api.API_SENDING_TIMEOUT

class NotificationBase:
    COMPLETE    = 'COMPLETE'
    ERROR       = 'ERROR'
    GENERAL     = 'GENERAL'
    WARNING     = 'WARNING'
    def __init__(self, backend_endpoint : str, bio_jwt : str, module_id : int):
        self.backend_url    = backend_endpoint
        self.bio_jwt        = bio_jwt
        self.module_id      = module_id
    
    @api_to_django_execute
    def create(
        self, title : str, content : str, type : str = GENERAL, timeout : int = API_SENDING_TIMEOUT
    ) -> requests.Response:
        data    = {
            'title' : title, 'content' : content, 'module' : self.module_id,
            'type' : type
        }
        return requests.post(
            url = f'{self.backend_url}bio/notification/',
            data = data,
            headers = {'Authorization' : f'Token {self.bio_jwt}'},
            timeout=timeout,
        )
            

class Notification:
    NOTIFICATION_ENDPOINT   = 'notification/all/'
    def __init__(self, module_id : int):
        endpoint            = get_backend_endpoint()
        jwt                 = get_jwt()
        self._notification  = NotificationBase(endpoint, jwt, module_id)
    def notification(self) -> NotificationBase:
        return self._notification