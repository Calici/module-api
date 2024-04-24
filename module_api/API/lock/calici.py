# Library Imports
from datetime import datetime
from pathlib import Path

# Local Imports
from .file import LockIO, LockFileManager
from .field import LockField
from .list import ListField
from .section import LockSection
from module_api.common.other_lib import get_current_time
from .utils import recursive_merge
from .type import SpreadKwargs
from typing_extensions import Dict, Any
from module_api.API.patterns import FileLock
import yaml

# Conditions of the running process
class LockIOStatusType:
    STOP                = 'STOP'
    INIT                = 'INIT'
    COMPLETE            = 'COMPLETE'
    RUNNING             = 'RUNNING'
    PREPARE_CANCEL      = 'PREPARE_CANCEL'
    PRE_INIT            = 'PRE_INIT'
    ERROR               = 'ERROR'

class LockProcessType:
    # same name of folder modules.xxxx
    # flask_backend/backend/base/lockfile.py call f'modules.{self.header.process}.run'
    DOCKING     = 'ai_dock'
    PREPARE     = 'prep'
    DEEP_CALICI = 'deep_calici'
    CALICI_FOLD    = 'calici_fold'
    DEEP_CALICI_4DCNN = 'deep_calici_4dcnn'
    DEEP_CALICI_RESNET3D = 'deep_calici_resnet3d'

# Class GPU Stat
class GPUStatus(LockSection):
    gpu_id  = LockField(int, default = 0)
    thread  = LockField(int, default = 0)

# Status
class LockStatus(LockSection):
    # The status of the running runnable
    status      = LockField(str, default = LockIOStatusType.PRE_INIT)
    # Checks if the websocket is connected, this blocks out two users connecting
    # at the same time
    is_connected= LockField(bool, default = False)
    # The last time the lock file manager checks the lock  file
    last_check  = LockField(datetime, get_current_time())
    # When the process started
    start_time  = LockField(datetime, get_current_time())
    # If the initialization process is done, this prevents double initialization
    initialized = LockField(bool, default = False)

# Header of a lock file
class LockHeader(LockSection):
    process     = LockField(str, default = LockProcessType.DOCKING)
    workdir     = LockField(Path, default = Path('workdir'))
    sharedir    = LockField(Path, default = Path('sharedir'))
    module_id   = LockField(int, default = -1)
    log_path    = LockField(Path, default = Path())
    pid         = LockField(int, default = -1)
    gpu_blocks  = ListField(SpreadKwargs(GPUStatus), [])

class CaliciLockFileManager(LockFileManager):
    def __init__(self, file_path: Path):
        super().__init__(file_path)
        self.params_file_manager = LockFileManager(self.file_path.parent / 'params.yml')

    def from_file(self) -> Dict[str, Any]:
        all_but_params = super().from_file()
        all_but_params.update(self.params_file_manager.from_file())
        return all_but_params
    
    def write_changes_to_file(self, changes: Dict[str, Any]) -> Dict[str, Any]:
        params_changes = changes.pop('params', None)
        if params_changes is not None:
            merged_params = self.params_file_manager.write_changes_to_file(params_changes)
        else:
            merged_params = {}
        # At this point, it had been removed before. 
        merged_params.update(super().write_changes_to_file(changes))
        return merged_params

    def write_all_to_file(self, content: Dict[str, Any]):
        params = content.pop('params')
        self.params_file_manager.write_all_to_file(params)
        super().write_all_to_file(content)
class CaliciLock(LockIO):
    header      = LockHeader()
    status      = LockStatus()
    params      = LockField(dict, {})
    depends     = LockField(dict, {})
    __display_file_path__   = 'display'
    __error_file_path__     = 'errors.json'
    __reserved_file_path__  = '.reserved'
    DISPLAY_CHANGES_FILE    = 'changes.json'
    DISPLAY_MAIN_FILE       = 'main.json'
    def __init__(self, file_path : Path, **kwargs):
        super().__init__(file_path, file_manager = CaliciLockFileManager(file_path), **kwargs)
    
    # Get display file path
    def display_path(self) -> Path:
        return self.file_path.parent / self.__display_file_path__
    def params_path(self) -> Path:
        return self.file_path.parent / 'params.yml'
    # Get error file path
    def error_path(self) -> Path:
        return self.file_path.parent /self.__error_file_path__
    # changing status
    def change_status(self, status : str):
        if not self.file_exists():
            return
        if self.is_complete():
            return
        self.set(
            status  = {
                'status' : status,
                'last_check' : get_current_time()
            },
        )
    # Initialize displays
    def __init_display__(self):
        path            = self.display_path()
        path.mkdir(0o777, True, True)
    # Status control
    def pause(self): 
        self.change_status(LockIOStatusType.STOP)
    def stop(self): 
        self.change_status(LockIOStatusType.STOP)
    def complete(self): 
        self.change_status(LockIOStatusType.COMPLETE)
    def disconnect(self): 
        self.set(status = {'is_connected' : False})
    def connect(self): 
        self.set(status = {'is_connected' : True})
    def start(self): 
        self.change_status(LockIOStatusType.INIT)
    def error(self): 
        self.change_status(LockIOStatusType.ERROR)

    # Check process running state
    def is_running(self): 
        return self.status.status.get() == LockIOStatusType.RUNNING
    def is_complete(self): 
        return self.status.status.get() == LockIOStatusType.COMPLETE
    def is_stop(self): 
        return self.status.status.get() == LockIOStatusType.STOP
    def is_cancel(self): 
        return self.status.status.get() == LockIOStatusType.PREPARE_CANCEL
    def is_init(self): 
        return self.status.status.get() == LockIOStatusType.INIT
    def is_pre_init(self): 
        return self.status.status.get() == LockIOStatusType.PRE_INIT
    def is_error(self):
        return self.status.status.get() == LockIOStatusType.ERROR

    @staticmethod
    def default_log_path(workdir : Path):
        return workdir / CaliciLock.__reserved_file_path__ / 'v_log.txt'

    @staticmethod
    def lock_Path_from_dir(workdir : Path, filename : str):
        return workdir / CaliciLock.__reserved_file_path__ / filename