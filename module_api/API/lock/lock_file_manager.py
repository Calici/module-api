from typing_extensions import Dict, Any, Protocol, IO
from module_api.API.patterns import FileLock
from .utils import recursive_merge
import yaml
import pathlib
import json

class LockFileManager(Protocol):
    file_path : pathlib.Path
    def from_file(self) -> Dict[str, Any]:
        """
            Gets the full contents from a file.
        """
        ...
    def write_changes_to_file(self, changes : Dict[str, Any]) -> Dict[str, Any]:
        """
            Write only the changed part of the content to the file. This will mutate changes and
            return.
        """
        ...
    def write_all_to_file(self, changes : Dict[str, Any]) -> Dict[str, Any]:
        ...

class JsonLockFileManager(LockFileManager):
    def __init__(self, file_path: pathlib.Path):
        """
        This will initialize the LockFileManager and assigns two properties,
        file_path, file_lock
        """
        self.file_path = file_path
        self.file_lock = FileLock(self.file_path)

    def from_file(self) -> Dict[str, Any]:
        with self.file_lock.lock_shared() as f:
            return self.load(f)

    def write_changes_to_file(self, changes: Dict[str, Any]) -> Dict[str, Any]:
        file_contents = self.from_file()
        merged_contents = recursive_merge(changes, file_contents)
        with self.file_lock.lock() as f:
            self.dump(f, merged_contents)
        return merged_contents

    def write_all_to_file(self, content: Dict[str, Any]):
        """
        Write all of the contents to the file.
        """
        with self.file_lock.lock() as f:
            self.dump(f, content)
    
    def load(self, f : IO):
        return json.load(f)
    def dump(self, f : IO, content : Any):
        json.dump(content, f)

class YamlLockFileManager(LockFileManager):
    def __init__(self, file_path: pathlib.Path):
        """
        This will initialize the LockFileManager and assigns two properties,
        file_path, file_lock
        """
        self.file_path = file_path
        self.file_lock = FileLock(self.file_path)

    def from_file(self) -> Dict[str, Any]:
        with self.file_lock.lock_shared() as f:
            return self.load(f)

    def write_changes_to_file(self, changes: Dict[str, Any]) -> Dict[str, Any]:
        file_contents = self.from_file()
        merged_contents = recursive_merge(changes, file_contents)
        with self.file_lock.lock() as f:
            self.dump(f, merged_contents)
        return merged_contents

    def write_all_to_file(self, content: Dict[str, Any]):
        """
        Write all of the contents to the file.
        """
        with self.file_lock.lock() as f:
            self.dump(f, content)
    
    def load(self, f : IO):
        return yaml.safe_load(f)
    def dump(self, f : IO, content : Any):
        yaml.dump(content, f, default_flow_style = False)