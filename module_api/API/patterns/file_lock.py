"""
    The file lock implemented here will only work when used in the linux
    ecosystem or macos ecosystem and will not work on windows.
"""
from __future__ import annotations
from .with_pattern import WithPattern
from typing_extensions import IO
from module_api.API.file_lock import FileMutex
import pathlib

class FileLock:
    def __init__(self, target_file : pathlib.Path, is_binary : bool = False):
        self.target_file = target_file
        self.target_file.parent.mkdir(exist_ok = True, parents = True)
        self.is_binary = is_binary
        self.mutex = FileMutex(str(self.target_file))
    
    def lock(self) -> WithPattern[IO]:
        """
            Usage : 
            with FileLock(some_file).lock() as f:
        """
        return WithPattern( self._lock, self._unlock )

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
        if self.is_binary:
            try:
                return open(self.target_file, 'rb')
            except:
                self.mutex.unlock_shared()
                raise
        else:
            try:
                return open(self.target_file, 'r')
            except:
                self.mutex.unlock_shared()
                raise

    def _lock(self) -> IO:
        self.mutex.lock()
        if self.is_binary:
            try:
                return open(self.target_file, 'wb')
            except:
                self.mutex.unlock()
                raise
        else:
            try:
                return open(self.target_file, 'w')
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