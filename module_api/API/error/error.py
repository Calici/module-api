# Library Import
import json
from typing_extensions import IO

# API Import
import module_api.API.lock as lock
from module_api.API.display.component import Message

# Local Imports
class ErrorBuffer(lock.LockIO):
    errors = lock.ListField(lock.SpreadKwargs(Message), default = [])
    version = lock.LockField(type = str, default = "1.0")
    def __init__(self, lock : lock.CaliciLock, version : str = "1.0"):
        super().__init__(lock.error_path(), version = version)
    # Override saving and loading to json
    def loader(self, f: IO[str]):
        return json.load(f)
    def dumper(self, f : IO[str], data : dict):
        return json.dump(data, f)
    # Others
    def add_entry(self, title : str, content : str, commit : bool = True):
        self.errors.append({
            'title' : title, 'content' : content
        })
        if commit:
            self.save()