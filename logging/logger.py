# Python Libraries
import logging
import pathlib

# Local Imports
from .formatters import *

# Logs to a file
## Handles file creation automatically
class FileLogger(logging.FileHandler):
    def __init__(self, 
        file_path : pathlib.Path, level_no : int = logging.WARNING
    ):
        file_path   = pathlib.Path(file_path)
        file_path.parent.mkdir(parents = True, exist_ok = True)
        self.level_no   = level_no
        super().__init__(file_path)
    
    def emit(self, record : logging.LogRecord):
        level_no    = record.levelno
        if level_no >= self.level_no:
            super().emit(record)


