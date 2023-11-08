import pathlib
from typing_extensions import \
    Union
# This parses the params into functions that we can use
class Params:
    def __init__(self, 
        params : Union[dict, None] = None, dirs : Union[dict, None] = None
    ):
        self._params    = params if params is not None else {}
        self._dirs      = dirs if dirs is not None else {}

    def set_dirs(self, dirs : dict):
        self._dirs  = dirs
    def set_params(self, params : dict):
        self._params= params

    # Getter Function because we cannot modify
    def params(self) -> dict:
        return self._params['params']

    # Getting a work directory
    def work_dir(self) -> pathlib.Path:
        return pathlib.Path(self._dirs['work_dir'])

    # Getting a shared directory
    def share_dir(self) -> pathlib.Path:
        return pathlib.Path(self._dirs['share_dir'])

    # Getting the module id
    def module_id(self) -> pathlib.Path:
        return self._params['module_id']

    # Dependencies Getting
    def depends(self) -> dict:
        return self._params['depends']

    def module_name(self) -> dict:
        return self._params['module_name']
    
    def use_queue(self) -> bool:
        return self._params.get('queue', False)

    def gpu_blocks(self) -> list:
        return self._params.get('gpu_blocks', [])