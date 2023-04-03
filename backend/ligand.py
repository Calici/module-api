import requests
from .utils import get_backend_endpoint, get_jwt


class LigandModuleUpdateError(Exception):
    def __init__(self, obj: requests.Response):
        self.obj = obj


class LigandAIDockModuleBase:
    BASE_ENDPOINT = 'bio/ligands/select/{module_id}/'

    def __init__(self, backend_endpoint: str, bio_jwt: str, module_id: int):
        self.endpoint = f'{backend_endpoint}{self.BASE_ENDPOINT.format(module_id = module_id)}'
        self.headers = {'Authorization': f'Token {bio_jwt}'}
        self.module_id = module_id

    def select(self, count:int, library:int, category:int):
        post_req = requests.post(
            url=self.endpoint,
            data={
                'count' : count,
                'library' : library,
                'category' : category,
            },
            headers=self.headers
        )
        if post_req.status_code == 200:
            return post_req
        else:
            raise LigandModuleUpdateError(post_req.text)

class LigandAIDockModule:
    def __init__(self, module_id: int):
        endpoint = get_backend_endpoint()
        jwt = get_jwt()
        self._ligand = LigandAIDockModuleBase(endpoint, jwt, module_id)

    def ligand(self) -> LigandAIDockModuleBase:
        return self._ligand
