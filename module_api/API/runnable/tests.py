import unittest
from module_api.API.lock import CaliciLock
from module_api.API.test import generate_test_fd
from .runnable import Runnable
import shutil

class TestLock(CaliciLock):
    pass

class TestRunnable(Runnable[TestLock]):
    lock_type = TestLock

class TestRun(unittest.TestCase):
    def test_if_running(self):
        with generate_test_fd() as tmp_fd:
            lock_file = CaliciLock(tmp_fd / 'tmp_file')
            runnable = TestRunnable(lock_path = lock_file.file_path)
            shutil.rmtree(tmp_fd)