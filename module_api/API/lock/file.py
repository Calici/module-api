# Library Imports
import yaml
import pathlib
from typing_extensions import IO
# Local Imports
from .section import LockSection
from .utils import recursive_merge
from module_api.API.patterns import FileLock

class LockIO(LockSection):
    FORCE_READ_TIMEOUT  = 0.2
    FORCE_READ_TRIAL    = 10
    def __init__(self, file_path   : pathlib.Path, **kwargs):
        # Initialize things important for FileIO
        self.file_path = pathlib.Path(file_path)
        new_file = not self.file_path.exists()
        # Prevent multi threaded and multi processed error.
        self._fs_lock = FileLock(self.file_path)
        super().__init__(**kwargs)
        # File IO
        self._init_file(new_file, self.file_path)
        self.set_value(kwargs, False)

    # Initialize the file for use with the API
    def _init_file(self, new : bool, path : pathlib.Path):
        if new:
            path.parent.mkdir(exist_ok = True, parents = True)
            with self._fs_lock.lock() as f: 
                self.dumper(f, self.serialize())
        else:
            self._init_value()

    # Set value with saving to file
    def set(self, **kwargs):
        super().set(**kwargs)
        self._save_file()

    # save the file values
    def _save_file(self):
        # Build dictionary
        build_dict  = self.serialize_changes()
        # Block update if empty
        if build_dict == {}:
            return 
        conf = self._file_values()
        conf = recursive_merge(build_dict, conf)
        with self._fs_lock.lock() as f:
            self.dumper(f, conf)
        # Set the values from the file
        self.set_value(conf, False)
        self.flush()

    def save(self):
        self._save_file()

    # Get values from file and save it
    def _file_values(self) -> dict:
        with self._fs_lock.lock_shared() as f:
            conf    = self.loader(f)
        return conf

    # Initialize values
    def _init_value(self):
        conf    = self._file_values()
        self.set_value(conf, False)

    # Reload Config
    def reload(self):
        if self.file_exists():
            self._init_value()

    # Check file exists
    def file_exists(self):
        return self.file_path.exists()

    # OVERRIDE THIS TO CHANGE THE LOADER AND THE DUMPER OR HOW THEY WORK
    def loader(self, f : IO[str]):
        return yaml.safe_load(f)
    
    def dumper(self, f : IO[str], data : dict):
        return yaml.dump(data, f, default_flow_style = False)