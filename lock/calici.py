# Library Imports
from datetime import datetime
from pathlib import Path

# Local Imports
from .file import LockIO
from .field import LockField, ListField
from .section import LockSection
from common.other_lib import get_current_time

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
    workdir     = LockField(Path, default = Path('../workdir'))
    sharedir    = LockField(Path)
    module_id   = LockField(int)
    log_path    = LockField(Path)
    pid         = LockField(int)
    gpu_blocks  = ListField(GPUStatus(), [])

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
    # Get display file path
    def display_path(self) -> Path:
        return self.header['workdir'].get() \
            / self.__reserved_file_path__ \
            / self.__display_file_path__
    # Get error file path
    def error_path(self) -> Path:
        return self.header['workdir'].get() \
            / self.__reserved_file_path__ \
            / self.__error_file_path__
    # changing status
    def change_status(self, status : LockIOStatusType):
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
    def pause(self): self.change_status(LockIOStatusType.STOP)
    def stop(self): self.change_status(LockIOStatusType.STOP)
    def complete(self): self.change_status(LockIOStatusType.COMPLETE)
    def disconnect(self): self.set(status = {'is_connected' : False})
    def connect(self): self.set(status = {'is_connected' : True})
    def start(self): self.change_status(LockIOStatusType.INIT)
    def error(self): self.change_status(LockIOStatusType.ERROR)

    # Check process running state
    def is_running(self): return self.status.status == LockIOStatusType.RUNNING
    def is_complete(self): return self.status.status == LockIOStatusType.COMPLETE
    def is_stop(self): return self.status.status == LockIOStatusType.STOP
    def is_cancel(self): return self.status.status == LockIOStatusType.PREPARE_CANCEL
    def is_init(self): return self.status.status == LockIOStatusType.INIT
    def is_pre_init(self): return self.status.status == LockIOStatusType.PRE_INIT
    def is_error(self):
        return self.status.status == LockIOStatusType.ERROR

    @staticmethod
    def default_log_path(workdir : Path):
        return workdir / CaliciLock.__reserved_file_path__ / 'v_log.txt'
