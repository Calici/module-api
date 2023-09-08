# Library Import
import pathlib
import json
from typing import IO
import logging
from typing import TypeVar, Generic

# API Import
import API.lock as lock

# Local Imports
from .component import BaseComponent

class BaseDisplay(lock.LockIO):
    # Display Types
    NO_TABLE    = 0
    ONE_TABLE   = 1

    dtype = lock.LockField(type = int, default = 0)
    component = BaseComponent()
    # Initiation with lock
    def __init__(self, lock : lock.CaliciLock, **kwargs):
        changes_path    = BaseDisplay.changes_file_path(lock.display_path())
        main_path       = BaseDisplay.full_file_path(lock.display_path())
        self.change_path= changes_path
        super().__init__(main_path, **kwargs)
        self.lockfile   = lock
    
    # Override loading to json
    def loader(self, f: IO[str]):
        return json.load(f)
    def dumper(self, f : IO[str], data : dict):
        return json.dump(data, f)

    @staticmethod
    def full_file_path(dir : pathlib.Path) -> pathlib.Path:
        return dir / lock.CaliciLock.DISPLAY_MAIN_FILE

    @staticmethod
    def changes_file_path(dir : pathlib.Path) -> pathlib.Path:
        return dir / lock.CaliciLock.DISPLAY_CHANGES_FILE

    def save_changes_file(self, content : dict):
        fname           = self.change_path.stem
        counter         = 0
        change_path     = self.change_path
        while change_path.exists():
            change_path     = self.change_path.parent / f'{fname}_{counter}.json'
            counter += 1
        with open(change_path, 'w') as f:
            self.dumper(f, content)
    
    def _save_file(self):
        """
            Overriden to save to a changes file as well.
        """
        build_dict  = self.serialize_changes()\
        # Write into the changes file as a queue
        self.lockfile.reload()
        if self.lockfile.status.is_connected:
            self._thread_lock.acquire()
            self.save_changes_file(build_dict)
            self._thread_lock.release()
        else:
        # Write all into a file
            super()._save_file()

T = TypeVar('T', bound = BaseComponent)
class Display(BaseDisplay, Generic[T]):
    component : T
    def __init__(self,
        lock        : lock.CaliciLock,
        dtype       : int,
        component   : T
    ):
        assert isinstance(dtype, int)
        assert isinstance(component, BaseComponent)

        self.component  = component
        super().__init__(lock, dtype = dtype)
        self.set(dtype = dtype)

    # This is to set the status of the display
    def status_complete(self):
        self.component.set(status = lock.LockIOStatusType.COMPLETE)
        self.save()

    def status_run(self):
        self.component.set(status = lock.LockIOStatusType.RUNNING)
        self.save()

    def status_stop(self):
        self.component.set(status = lock.LockIOStatusType.STOP)
        self.save()

    def status_error(self):
        self.component.set(status = 'ERROR')
        self.save()