# Library stuff
import pathlib
import json
from typing_extensions import IO
from typing_extensions import \
    TypeVar, \
    Generic

# API Import
import module_api.API.lock as lock


T = TypeVar('T', bound = lock.LockSection)
class Display(lock.LockIO, Generic[T]):
    dtype = lock.LockField(type = int, default = 0)
    component : T
    def __init__(self, lock : lock.CaliciLock, component : T, **kwargs):
        self.component = component
        super().__init__(self.full_file_path(lock.display_path()), **kwargs)
        self.lockfile = lock
        self.changes_path = self.changes_file_path(lock.display_path())

    # Override Loading To JSON Loading
    def loader(self, f: IO[str]):
        return json.load(f)
    def dumper(self, f : IO[str], data : dict):
        return json.dump(data, f)
    
    # Save Changes to a new File all the time
    def save_changes_file(self, content : dict):
        fname = self.changes_path.stem
        counter = 0
        parent_path = self.changes_path.parent
        change_path = parent_path / f'{fname}_{counter}.json'
        while change_path.exists():
            change_path = parent_path / f'{fname}_{counter}.json'
            counter += 1
        with open(change_path, 'w') as f:
            self.dumper(f, content)
    def _save_file(self):
        """
            Overriden to save to a changes file as well.
        """
        build_dict = self.serialize_changes()
        # Write into the changes file as a queue
        self.lockfile.reload()
        is_connected = self.lockfile.status.is_connected.get()
        if is_connected:
            self._thread_lock.acquire()
            self.save_changes_file(build_dict)
            self._thread_lock.release()
        lock.LockIO._save_file(self)

    # Set Certain Fields
    def status_complete(self):
        self.set(
            component = {'status' : lock.LockIOStatusType.COMPLETE}
        )
    def status_run(self):
        self.set(
            component = {'status' : lock.LockIOStatusType.RUNNING}
        )
    def status_stop(self):
        self.set(
            component = {'status' : lock.LockIOStatusType.STOP}
        )
    def status_error(self):
        self.set(
            component = {'status' : lock.LockIOStatusType.ERROR}
        )

    @staticmethod
    def full_file_path(dir : pathlib.Path) -> pathlib.Path:
        return dir / lock.CaliciLock.DISPLAY_MAIN_FILE

    @staticmethod
    def changes_file_path(dir : pathlib.Path) -> pathlib.Path:
        return dir / lock.CaliciLock.DISPLAY_CHANGES_FILE
    
    def __del__(self):
        """
            Delete change_xxx.json file in display folder. 
            This is called just in case a lot of data is not read after it 
            has been generated.
        """
        parent_path = self.changes_path.parent
        fname = self.changes_path.stem
        files = list(parent_path.glob(f"{fname}_*.json"))
        tmp_files = []
        for file in files:
            try:
                tmp_files.append({
                    'file':file,
                    'order': int(file.stem.split("_")[-1])
                })
            except Exception:
                pass

        tmp_files.sort(key=lambda x: x['order'])
        # delete files except last 10
        for item in tmp_files[:-10]:
            try:
                item['file'].unlink()
            except Exception:
                pass
