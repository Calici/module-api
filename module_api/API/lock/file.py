# Library Imports
import yaml
import pathlib
from typing_extensions import Dict, Any, Union, IO

# Local Imports
from .section import LockSection
from .utils import recursive_merge
from module_api.API.patterns import FileLock


class LockFileManager:
    def __init__(self, file_path: pathlib.Path):
        """
        This will initialize the LockFileManager and assigns two properties,
        file_path, file_lock
        """
        self.file_path = file_path
        self.file_lock = FileLock(self.file_path)

    def from_file(self) -> Dict[str, Any]:
        """
        Gets the full contents from a file.
        """
        with self.file_lock.lock_shared() as f:
            return self.load(f)

    def write_changes_to_file(self, changes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Write only the changed part of the content to the file. This will mutate changes and
        return.
        """
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


class LockIO(LockSection):
    FORCE_READ_TIMEOUT = 0.2
    FORCE_READ_TRIAL = 10

    def __init__(
        self,
        file_path: Union[pathlib.Path, str],
        file_manager: Union[LockFileManager, None] = None,
        **kwargs,
    ):
        # Initialize File Path
        if isinstance(file_path, str):
            file_path = pathlib.Path(file_path)
        self.file_path = file_path

        # Initialize the manager
        if file_manager is None:
            file_manager = LockFileManager(self.file_path)
        self.file_manager = file_manager

        # Check if a new file is going to be created
        super().__init__(**kwargs)
        # Initialize the current lock state.
        self._init_file(**kwargs)

    def _init_file(self, **kwargs):
        """
        Synchronizes between the state of the file and the current state of the object
        """
        if self.file_path.exists():
            file_values = self.file_manager.from_file()
            file_values.update(kwargs)
            # Write the current values after overriden by kwargs
            self.set_value(file_values, False)
        else:
            # Kwargs have been written to self.
            value_to_write = self.serialize()
            self.file_manager.write_all_to_file(value_to_write)

    def reload(self):
        """
        Reloads the lock file from the file.
        """
        if self.file_exists():
            self.set_value(self.file_manager.from_file(), False)

    # Set value with saving to file
    def set(self, **kwargs):
        super().set(**kwargs)
        self.save()

    def save(self):
        # Build dictionary
        build_dict = self.serialize_changes()
        # Block update if empty
        if build_dict == {}:
            return
        merged_value = self.file_manager.write_changes_to_file(build_dict)
        self.set_value(merged_value, False)
        self.flush()

    # Check file exists
    def file_exists(self):
        return self.file_path.exists()
