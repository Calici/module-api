import requests
from .utils import get_backend_endpoint, get_jwt

class NotificationError(Exception):
    def __init__(self, obj : requests.Response):
        self.obj    = obj
class NotificationCreateError(NotificationError): pass
class NotificationUpdateError(NotificationError): pass
class NotificationDeleteError(NotificationError): pass

class NotificationBase:
    COMPLETE    = 'COMPLETE'
    ERROR       = 'ERROR'
    GENERAL     = 'GENERAL'
    WARNING     = 'WARNING'
    def __init__(self, backend_endpoint : str, bio_jwt : str, module_id : int):
        self.backend_url    = backend_endpoint
        self.bio_jwt        = bio_jwt
        self.module_id      = module_id
    def create(
        self, title : str, content : str, type : str = GENERAL
    ) -> requests.Response:
        data    = {
            'title' : title, 'content' : content, 'module' : self.module_id,
            'type' : type
        }
        post_req    = requests.post(
            url = f'{self.backend_url}bio/notification/',
            data = data,
            headers = {'Authorization' : f'Token {self.bio_jwt}'}
        )
        if post_req.status_code == 200:
            return post_req
        else: 
            raise NotificationCreateError(post_req)
    def update(self, notification_id : int, **kwargs) -> requests.Response:
        post_req    = requests.post(
            url = f'{self.backend_url}bio/notification/{notification_id}',
            data = kwargs,
            headers = {'Authorization' : f'Token {self.bio_jwt}'}
        )
        if post_req.status_code == 200: return post_req
        else: raise NotificationUpdateError(post_req)
    def delete(self, notification_id : int) -> requests.Response:
        post_req    = requests.delete(
            url = f'{self.backend_url}bio/notification/{notification_id}',
            headers = {'Authorization' : f'Token {self.bio_jwt}'}
        )
        if post_req.status_code == 200: return post_req
        else: raise NotificationDeleteError(post_req)

class Notification:
    NOTIFICATION_ENDPOINT   = 'notification/all/'
    def __init__(self, module_id : int):
        endpoint            = get_backend_endpoint()
        jwt                 = get_jwt()
        self._notification  = NotificationBase(endpoint, jwt, module_id)
    def notification(self) -> NotificationBase:
        return self._notification