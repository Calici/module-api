# Library Import
import json
from typing_extensions import IO, Literal

# API Import
import module_api.API.lock as lock

ErrorT = Literal["WARNING", "ERROR"]

class ErrorMessage(lock.LockSection):
    title = lock.LockField(type = str, default = '')
    content = lock.LockField(type = str, default = '')
    type = lock.LockField[ErrorT](type = str, default = 'ERROR')

class ErrorBufferStruct(lock.LockIO):
    """
        Contains only the structure of ErroBuffer with no associated
        implementation
    """
    errors = lock.ListField(lock.SpreadKwargs(ErrorMessage), default = [])
    version = lock.LockField(type = str, default = "2.0")
# Local Imports
class ErrorBuffer(ErrorBufferStruct):
    def __init__(self, lock : lock.CaliciLock, version : str = "2.0"):
        super().__init__(lock.error_path(), version = version)
    # Override saving and loading to json
    def loader(self, f: IO[str]):
        return json.load(f)
    def dumper(self, f : IO[str], data : dict):
        return json.dump(data, f)
    # Others
    def add_entry(self, 
        title : str, content : str, type : ErrorT = "ERROR", 
        commit : bool = True
    ):
        """
            Adds entry to the error file, 
            type : "WARNING" or "ERROR"
        """
        self.errors.append(
            { 'title' : title, 'content' : content, 'type' : type }
        )
        if commit:
            self.save()