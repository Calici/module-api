import requests
from .utils import get_backend_endpoint, get_jwt
from .utils.decorator import backend_api_call
from typing_extensions import TypedDict, List

ChoiceT = TypedDict("ChoiceT", {"name": str, "level": int})
UserLevelT = TypedDict("UserLevelT", {
    "level" : str, 
    "choices" : List[ChoiceT]
})

class UserAPI:
    def __init__(self, module_id : int):
        self.endpoint = '{0}bio/module/{1}'.format(get_backend_endpoint(), module_id)
        self.headers = {'Authorization' : 'Token {0}'.format(get_jwt())}
    
    def user_level(self) -> UserLevelT:
        return self._query_user_level().json()

    @backend_api_call()
    def _query_user_level(self):
        endpoint = f'{self.endpoint}/runner_level'
        return requests.get(
            url = endpoint, 
            headers = self.headers
        )