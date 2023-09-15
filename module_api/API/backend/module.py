# Library Imports
import module_api.API.lock as lock
import pathlib

from .utils import get_backend_endpoint, get_jwt, RequestAutoRefresh
from typing import \
  Union, \
  Literal, \
  TypeVar, \
  Generic, \
  Dict, \
  Callable
import shutil

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
    def convert_to_shared(self, 
        work_dir : pathlib.Path, 
        share_dir : pathlib.Path                      
    ):
        new_contents = {}
        for field_name, field in self.items():
            value = field.get()
            if isinstance(value, pathlib.Path) and work_dir in value.parents:
                new_contents[field_name] = \
                    share_dir / value.relative_to(work_dir)
        self.set_value(new_contents)
    def convert_to_work(self, 
        work_dir : pathlib.Path, 
        share_dir : pathlib.Path
    ):
        self.convert_to_shared(share_dir, work_dir)
    def create_symlnk(self, 
        work_dir : pathlib.Path, share_dir : pathlib.Path                
    ):
        for field in self.values():
            path = field.get()
            if isinstance(path, pathlib.Path):
                if share_dir in path.parents:
                    share_path = path
                    work_path = work_dir / path.relative_to(share_dir)
                    self.__create_symlnk_ignore_errors(work_path, share_path)
                elif work_dir in path.parents:
                    share_path = share_dir / path.relative_to(work_dir)
                    work_path = path
                    self.__create_symlnk_ignore_errors(work_path, share_path)
                    
    def __create_symlnk_ignore_errors(
        self, src : pathlib.Path, target : pathlib.Path
    ):
        if not target.parent.exists():
            target.parent.mkdir(0o777, True, True)
        if target.is_symlink(): target.unlink()
        elif target.is_file(): target.unlink()
        elif target.is_dir(): shutil.rmtree(target)
        target.symlink_to(src)
            
    
    

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
