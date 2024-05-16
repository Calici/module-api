"""
    The file lock implemented here will only work when used in the linux
    ecosystem or macos ecosystem and will not work on windows.
"""
from __future__ import annotations
from .with_pattern import WithPattern
from typing_extensions import IO, Literal
from module_api.API.file_lock import FileMutex
import pathlib

class FileLock:
    def __init__(self, target_file : pathlib.Path, is_binary : bool = False):
        self.target_file = target_file
        self.target_file.parent.mkdir(exist_ok = True, parents = True)
        self.is_binary = is_binary
        self.mutex = FileMutex(str(self.target_file))
    
    def lock(self, mode : Literal['w', 'a', 'a+'] = 'w') -> WithPattern[IO]:
        """
            Usage : 
            with FileLock(some_file).lock() as f:
        """
        return WithPattern( lambda: self._lock(mode), self._unlock )
    
    def lock_shared(self) -> WithPattern[IO]:
        """
            Usage : 
            with FileLock(some_file).lock_shared() as f:
                pass
        """
        return WithPattern( self._lock_shared, self._unlock_shared)

    def _lock_shared(self) -> IO:
        """
            Internal Locks that guarantee exception freedom for file locking. 
        """
        self.mutex.lock_shared()
        mode = 'rb' if self.is_binary else 'r'
        try:
            return open(self.target_file, mode)
        except:
            self.mutex.unlock_shared()
            raise

    def _lock(self, mode : str) -> IO:
        self.mutex.lock()
        mode = f'{mode}b' if self.is_binary else mode
        try:
            return open(self.target_file, mode)
        except:
            self.mutex.unlock()
            raise
        
    def _unlock_shared(self, io : IO):
        """
            When the reader
        """
        self.mutex.unlock_shared()
        io.close()
    
    def _unlock(self, io : IO):
        self.mutex.unlock()
        io.close()