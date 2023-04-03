import requests
from .utils import get_backend_endpoint, get_jwt


class TokenModuleUpdateError(Exception):
    def __init__(self, obj: requests.Response):
        self.obj = obj


class TokenModuleBase:
    BASE_ENDPOINT = 'bio/token/{module_id}/'

    def __init__(self, backend_endpoint: str, bio_jwt: str, module_id: int):
        self.endpoint = f'{backend_endpoint}{self.BASE_ENDPOINT.format(module_id = module_id)}'
        self.headers = {'Authorization': f'Token {bio_jwt}'}
        self.module_id = module_id

    def use(self, amount: int):
        post_req = requests.post(
            url=self.endpoint,
            data={
                'update_type': 'use',
                'used': amount
            },
            headers=self.headers
        )
        if post_req.status_code == 200:
            return post_req
        else:
            raise TokenModuleUpdateError(post_req.text)

    def set(self, amount: int):
        post_req = requests.post(
            url=self.endpoint,
            data={
                'update_type': 'set',
                'used': amount
            },
            headers=self.headers
        )
        if post_req.status_code == 200:
            return post_req
        else:
            raise TokenModuleUpdateError(post_req.text)



class TokenModule:
    def __init__(self, module_id: int):
        endpoint = get_backend_endpoint()
        jwt = get_jwt()
        self._token = TokenModuleBase(endpoint, jwt, module_id)

    def token(self) -> TokenModuleBase:
        return self._token
