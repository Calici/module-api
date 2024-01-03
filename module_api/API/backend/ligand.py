import requests
from .utils import get_backend_endpoint, get_jwt
from .utils.decorator import backend_api_call
from module_api.API.backend.constants import API_SENDING_TIMEOUT


class LigandLibraryAPI:
    def __init__(self, module_id : int):
        self.endpoint = '{0}bio/ligands/select/{1}/'.format(
            get_backend_endpoint(), module_id
        )
        self.headers = {'Authorization' : 'Token {0}'.format(get_jwt())}
    @backend_api_call()
    def select(self, count : int, library : int, category : int):
        return requests.post(
            url = self.endpoint, 
            data = {
                'count' : count, 'library' : library, 'category' : category
            },
            headers = self.headers,
            timeout = API_SENDING_TIMEOUT
        )
