# Library Imports
import yaml
import pathlib
import threading
import logging
from typing import IO
import time

# Local Imports
from .section import LockSection
from .utils import recursive_merge

class LockIO(LockSection):
    FORCE_READ_TIMEOUT  = 0.2
    FORCE_READ_TRIAL    = 10
    def __init__(self,
        file_path   : pathlib.Path,
        **kwargs
    ):
        # Initialize things important for FileIO
        self.file_path  = pathlib.Path(file_path)
        new_file        = not self.file_path.exists()
        # Initialize the LockIO as a secti on
        super().__init__(**kwargs)
        self.process    = None
        # Prevent multi thread error
        self._thread_lock   = threading.Lock()
        # File IO
        self._init_file(new_file, self.file_path)

    # Initialize the file for use with the API
    def _init_file(self, new : bool, path : pathlib.Path):
        if new:
            path.parent.mkdir(exist_ok = True, parents = True)
            self._thread_lock.acquire()
            with open(path, 'w') as f: 
                self.dumper(f, self.serialize())
            self._thread_lock.release()
        else:
            self._init_value(path)

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
        conf        = self._file_values(self.file_path)
        conf        = recursive_merge(build_dict, conf)
        self._thread_lock.acquire()
        with open(self.file_path, 'w') as f:
            self.dumper(f, conf)
        self._thread_lock.release()
        # Set the values from the file
        self.set_value(conf, False)
        self.flush()

    def save(self):
        self._save_file()

    # Get values from file and save it
    def _file_values(self, path : pathlib.Path) -> dict:
        with open(path, 'r') as f:
            conf    = self.force_loader(f)
        return conf

    # Initialize values
    def _init_value(self, path : pathlib.Path):
        conf    = self._file_values(path)
        self.set_value(conf, False)

    # Reload Config
    def reload(self):
        if self.file_exists():
            self._init_value(self.file_path)

    # Check file exists
    def file_exists(self):
        return self.file_path.exists()

    # OVERRIDE THIS TO CHANGE THE LOADER AND THE DUMPER OR HOW THEY WORK
    def loader(self, f : IO[str]):
        return yaml.safe_load(f)
    
    def dumper(self, f : IO[str], data : dict):
        return yaml.dump(data, f, default_flow_style = False)
    
    def force_loader(self, f : IO[str]) -> dict:
        for i in range(self.FORCE_READ_TRIAL):
            try:
                loaded  = self.loader(f)
                if loaded: return loaded
                continue
            except:
                time.sleep(self.FORCE_READ_TIMEOUT)
        # Final Chance
        logging.warn("Loading OLD LOCKDATA. If error occurs.")
        return self.serialize()