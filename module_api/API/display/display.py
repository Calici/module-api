# Library stuff
import pathlib
import json
from typing_extensions import TypeVar, Generic, Dict, Any, IO

# API Import
import module_api.API.lock as lock
from module_api.API.patterns import FileLock


class DisplayFileManager(lock.LockFileManager):
    def __init__(self, file_path: pathlib.Path):
        super().__init__(file_path)
        # We will protect the changes set with a lock file.
        self.changes_base = self.file_path.parent / "changes"
        self.fname = self.changes_base.stem
        self.changes_lock = FileLock(self.changes_base)

    def write_incr_changes(self, changes: Dict[str, Any]):
        counter = 0
        change_path = self.changes_base.parent / f"{self.fname}_{counter}"
        parent_path = self.changes_base.parent

        # Protect the changes file dumping with a lock
        with self.changes_lock.lock():
            while change_path.exists():
                change_path = parent_path / f"{self.fname}_{counter}"
                counter += 1
            with open(change_path, "w") as f:
                self.dump(f, changes)

    def write_changes_to_file(self, changes: Dict[str, Any]) -> Dict[str, Any]:
        self.write_incr_changes(changes)
        return super().write_changes_to_file(changes)

    def write_all_to_file(self, content: Dict[str, Any]):
        self.write_incr_changes(content)
        super().write_all_to_file(content)
        
    def load(self, f: IO):
        return json.load(f)

    def dump(self, f : IO, content : Any):
        json.dump(content, f)
        


T = TypeVar("T", bound=lock.LockSection)


class Display(lock.LockIO, Generic[T]):
    dtype = lock.LockField(type=int, default=0)
    component: T

    def __init__(self, lock: lock.CaliciLock, component: T, **kwargs):
        self.component = component
        file_path = self.full_file_path(lock.display_path())
        super().__init__(
            self.full_file_path(lock.display_path()),
            file_manager=DisplayFileManager(file_path),
            **kwargs,
        )
        self.lockfile = lock
        self.changes_path = self.changes_file_path(lock.display_path())

    # Set Certain Fields
    def status_complete(self):
        self.set(component={"status": lock.LockIOStatusType.COMPLETE})

    def status_run(self):
        self.set(component={"status": lock.LockIOStatusType.RUNNING})

    def status_stop(self):
        self.set(component={"status": lock.LockIOStatusType.STOP})

    def status_error(self):
        self.set(component={"status": lock.LockIOStatusType.ERROR})

    @staticmethod
    def full_file_path(dir: pathlib.Path) -> pathlib.Path:
        return dir / lock.CaliciLock.DISPLAY_MAIN_FILE

    @staticmethod
    def changes_file_path(dir: pathlib.Path) -> pathlib.Path:
        return dir / lock.CaliciLock.DISPLAY_CHANGES_FILE
