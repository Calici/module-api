# Library Imports
import module_api.API.lock as lock
import pathlib

from .utils import get_backend_endpoint, get_jwt, RequestAutoRefresh
from typing import \
  Union, \
  Literal, \
  TypeVar, \
  Generic, \
  Type, \
  Dict, \
  Callable

class ModuleStatus:
    """
      Enumerates Module Status
    """
    INIT    = 'INIT'
    LOADING = 'LOADING'
    COMPLETE= 'COMPLETE'
    STOP    = 'STOP'
    ERROR   = 'ERROR'
    Type = Union[
        Literal['INIT'], Literal['LOADING'], Literal['COMPLETE'], 
        Literal['STOP'], Literal['ERROR']
    ]

class ModuleResult(lock.LockSection):
    def serialize_changes(self) -> dict:
        # Force Serialization:
        return self.serialize()
    

class ModuleSection(RequestAutoRefresh):
    status = lock.LockField[ModuleStatus.Type](str, ModuleStatus.INIT)
    progress = lock.LockField(float, 0.0)
    result_avail= lock.LockField(bool, False)
    allow_cont  = lock.LockField(bool, False)
    has_warning = lock.LockField(bool, False)
    lock        = lock.LockField(bool, False)
    results     = ModuleResult()

Section = TypeVar('Section', bound = lock.LockSection)
class ModuleAPI(Generic[Section]):
    def __init__(self,
      module_id : int, 
      Sect : Callable[[str, Dict], Section] = ModuleSection
    ):
        self.module = Sect(
            self.create_url_endpoint(module_id), 
            self.create_header()
        )

    def create_header(self) -> Dict:
        return {
            'Authorization' : 'Token {0}'.format(get_jwt())
        }

    def create_url_endpoint(self, module_id : int) -> str:
        return '{0}bio/module/{1}/'.format(get_backend_endpoint(), module_id)
