"""
    The file lock implemented here will only work when used in the linux
    ecosystem or macos ecosystem and will not work on windows.
"""
from __future__ import annotations
from .with_pattern import WithPattern
from typing_extensions import IO, Union
from threading import Lock, Condition
import fcntl
import pathlib

class FileLock:
    def __init__(self, target_file : pathlib.Path, is_binary : bool = False):
        self.target_file = target_file
        self.is_binary = is_binary
        self.target_lock_path = \
            self.target_file.parent / (self.target_file.stem + '.sys_lock')
        self.locked_f : Union[None, IO] = None
        
        # This is for single threaded syncing
        self.r_lock = Lock()
        self.r_cond = Condition(self.r_lock)
        self.r_count = 0
        self.w_lock = Lock()
    
    def lock(self) -> WithPattern[IO]:
        """
            Usage : 
            with FileLock(some_file).lock()
        """
        return WithPattern( self._lock, self._unlock )

    def lock_shared(self) -> WithPattern[IO]:
        """
            Usage : 
            with FileLock(some_file).lock_shared():
                pass
        """
        return WithPattern( self._shared_lock, self._shared_unlock )

    def _shared_lock(self) -> IO:
        with self.r_lock:
            self.r_count += 1
        self.locked_f = open(self.target_lock_path, 'w')
        fcntl.flock(self.locked_f.fileno(), fcntl.LOCK_SH)
        if self.is_binary:
            return open(self.target_file, 'rb')
        else:
            return open(self.target_file, 'r')

    def _lock(self) -> IO:
        # Wait for all readers to finish
        with self.r_lock:
            if self.r_count != 0:
                self.r_cond.wait()
        self.r_lock.acquire() # Prevent Reading
        self.w_lock.acquire() # Prevent Writing
        self.locked_f = open(self.target_lock_path, 'w')
        fcntl.flock(self.locked_f.fileno(), fcntl.LOCK_EX)
        if self.is_binary:
            return open(self.target_file, 'wb')
        else:
            return open(self.target_file, 'w')
        
    def _unlock_fs(self, io : IO):
        if self.locked_f:
            fcntl.flock(self.locked_f.fileno(), fcntl.LOCK_UN)
            self.locked_f.close()
        io.close()
        self.locked_f = None
        
    def _shared_unlock(self, io : IO):
        with self.r_lock:
            self.r_count -= 1
            if self.r_count == 0:
                self.r_cond.notify_all()
        self._unlock_fs(io)
    
    def _unlock(self, io : IO) :
        self._unlock_fs(io)
        self.r_lock.release()
        self.w_lock.release()