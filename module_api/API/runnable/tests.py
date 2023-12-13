import unittest
from module_api.API.lock import CaliciLock, LockIOStatusType
from module_api.API.test import generate_test_fd
from .compat.v0 import Runnable as Runnable_v0
from .runnable import Runnable, default_run
from .exceptions import \
    StopRunnable, \
    StopRunnableStatusError, \
    StopRunnableStatusStop
class TestLock(CaliciLock):
    pass

class TestRunnable(Runnable_v0[TestLock]):
    lock_type = TestLock

class TestRun(unittest.TestCase):
    def test_if_running(self):
        with generate_test_fd() as tmp_fd:
            lock_file = CaliciLock(tmp_fd / 'tmp_file')
            runnable = TestRunnable(lock_path = lock_file.file_path)
    
    def test_run_with_runnable_exception(self):
        class TestRunnable(Runnable[TestLock]):
            lock_type = TestLock
            def init(self):
                self.lock.change_status('RUNNING')
                raise StopRunnable("Hi Stopped")

            def re_init(self):
                self.init()
            
            def run(self):
                pass
            
            def stop(self):
                pass
        with generate_test_fd() as tmp_fd:
            lock_file = CaliciLock(tmp_fd / 'tmp_file')
            runnable = TestRunnable(lock_file.file_path)
            default_run(runnable)
            self.assertEqual(
                runnable.lock.status.status.get(), LockIOStatusType.STOP
            )
            
    def test_run_with_runnable_err_exception(self):
        class TestRunnable(Runnable[TestLock]):
            lock_type = TestLock
            def init(self):
                self.lock.change_status('RUNNING')
                raise StopRunnableStatusError("Hi Stopped")

            def re_init(self):
                self.init()
            
            def run(self):
                pass
            
            def stop(self):
                pass
        with generate_test_fd() as tmp_fd:
            lock_file = CaliciLock(tmp_fd / 'tmp_file')
            runnable = TestRunnable(lock_file.file_path)
            default_run(runnable)
            self.assertEqual(
                runnable.lock.status.status.get(), LockIOStatusType.ERROR
            )
            
        
