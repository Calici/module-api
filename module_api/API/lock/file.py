# Library Imports
import pathlib
from typing_extensions import Union

# Local Imports
from .section import LockSection
from .lock_file_manager import LockFileManager, YamlLockFileManager

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
            file_manager = YamlLockFileManager(file_path)
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
            # Ignore nonexistent fields, i.e. keep the fields we set but ignore fields set by others.
            self.set_value(file_values, False, True)
        else:
            # Kwargs have been written to self.
            value_to_write = self.serialize()
            self.file_manager.write_all_to_file(value_to_write)

    def reload(self):
        """
        Reloads the lock file from the file.
        """
        if self.file_exists():
            self.set_value(self.file_manager.from_file(), False, True)

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
        self.set_value(merged_value, False, True)
        self.flush()

    # Check file exists
    def file_exists(self):
        return self.file_path.exists()
