# Library Import
import json
from typing import IO

# API Import
import API.lock as lock
from API.display.component import Message

# Local Imports
class ErrorBuffer(lock.LockIO):
    errors  = lock.ListField(child = Message(), default = [])
    version = lock.LockField(type = str, default = "1.0")
    def __init__(self, lock : lock.CaliciLock, version : str = "1.0"):
        main_path   = lock.error_path()
        super().__init__(main_path, version = version)
    # Override saving and loading to json
    def loader(self, f: IO[str]):
        return json.load(f)
    def dumper(self, f : IO[str], data : dict):
        return json.dump(data, f)
    # Others
    def add_entry(self, title : str, content : str):
        errors  = self['errors'].get()
        errors.append({
            'title' : title, 'content' : content
        })
        self.set(errors = errors)