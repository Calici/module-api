import unittest
from module_api.API.lock import CaliciLock
from .runnable import Runnable
import pathlib
import os
import shutil

class TestLock(CaliciLock):
    pass

class TestRunnable(Runnable[TestLock]):
    lock_type = TestLock

class TestRun(unittest.TestCase):
    def test_if_running(self):
        tmp_fd = pathlib.Path('tmp/test_runnable').resolve()
        if not tmp_fd.is_dir():
            tmp_fd.mkdir(parents = True, exist_ok = True)
        os.chdir(tmp_fd)
        lock_file = CaliciLock(pathlib.Path('tmp_file'))
        runnable = TestRunnable(lock_path = lock_file.file_path)
        shutil.rmtree(tmp_fd)