from typing_extensions import Dict, Any, Protocol, IO
from module_api.API.patterns import FileLock
from .utils import recursive_merge
import yaml
import pathlib
import json

class ReaderWriter(Protocol):
    def load(self, f : IO) -> Any:
        ...
    def dump(self,f : IO, content : Any):
        ...

class YamlReaderWriter(ReaderWriter):
    def load(self, f : IO):
        return yaml.safe_load(f)
    def dump(self, f : IO, content : Any):
        return yaml.dump(content, f, default_flow_style = False)

class JsonReaderWriter(ReaderWriter):
    def load(self, f : IO):
        return json.load(f)
    def dump(self, f : IO, content : Any):
        return json.dump(content, f)
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

class SimpleFileManager(LockFileManager):
    def __init__(self, file_path: pathlib.Path, reader_writer : ReaderWriter):
        """
        This will initialize the LockFileManager and assigns two properties,
        file_path, file_lock
        """
        self.file_path = file_path
        self.file_lock = FileLock(self.file_path)
        self.reader_writer = reader_writer

    def from_file(self) -> Dict[str, Any]:
        with self.file_lock.lock_shared() as f:
            return self.reader_writer.load(f)

    def write_changes_to_file(self, changes: Dict[str, Any]) -> Dict[str, Any]:
        with self.file_lock.lock('a+') as f:
            # Point to starting position for loading
            f.seek(0)
            file_contents = self.reader_writer.load(f)
            merged_contents = recursive_merge(changes, file_contents)
            # Truncate file
            f.seek(0)
            f.truncate(0)
            self.reader_writer.dump(f, merged_contents)
        return merged_contents

    def write_all_to_file(self, content: Dict[str, Any]):
        """
        Write all of the contents to the file.
        """
        with self.file_lock.lock() as f:
            self.reader_writer.dump(f, content)

def JsonLockFileManager(file_path : pathlib.Path):
    """
        Returns a SimpleFileManager with a JSON Reader Writer
    """
    return SimpleFileManager(file_path, JsonReaderWriter())
def YamlLockFileManager(file_path : pathlib.Path):
    """
        Returns a SimpleFileManager with a Yaml Reader writer
    """
    return SimpleFileManager(file_path, YamlReaderWriter())