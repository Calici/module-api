# Library Import
import json
from typing_extensions import IO, Literal

# API Import
import module_api.API.lock as lock

ErrorT = Literal["WARNING", "ERROR"]


class ErrorMessage(lock.LockSection):
    title = lock.LockField(type=str, default="")
    content = lock.LockField(type=str, default="")
    type = lock.LockField[ErrorT](type=str, default="ERROR")

class ErrorFileManager(lock.LockFileManager):
    def load(self, f: IO):
        return json.load(f)
    def dump(self, f: IO, content):
        json.dump(content, f)


# Local Imports
class ErrorBuffer(lock.LockIO):
    errors = lock.ListField(lock.SpreadKwargs(ErrorMessage), default=[])
    version = lock.LockField(type=str, default="2.0")
    def __init__(self, lock: lock.CaliciLock, version: str = "2.0"):
        super().__init__(
            lock.error_path(),
            file_manager=ErrorFileManager(lock.error_path()),
            version=version,
        )

    # Others
    def add_entry(
        self, title: str, content: str, type: ErrorT = "ERROR", commit: bool = True
    ):
        """
        Adds entry to the error file,
        type : "WARNING" or "ERROR"
        """
        self.errors.append({"title": title, "content": content, "type": type})
        if commit:
            self.save()
