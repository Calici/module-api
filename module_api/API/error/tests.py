from .error import ErrorBuffer
from module_api.API.test import generate_test_fd
from module_api.API.lock import CaliciLock
import unittest
import pathlib
import json

class TestError(unittest.TestCase):
    def test_dumping(self):
        with generate_test_fd() as tmp_fd:
            lock_file = CaliciLock(
                tmp_fd / 'default.lock', 
                header = {
                    'workdir' : pathlib.Path(tmp_fd / 'workdir')
                }
            )
            buffer = ErrorBuffer(lock_file)
            buffer.add_entry("Error", "Error")
            with open(buffer.file_path, 'r') as f:
                content = json.load(f)
                error = content['errors'][0]
                self.assertEqual(error['type'], 'ERROR')
                self.assertEqual(error['title'], 'Error')
                self.assertEqual(error['content'], 'Error')


    def test_warning_test(self):
        with generate_test_fd() as tmp_fd:
            lock_file = CaliciLock(
                tmp_fd / 'default.lock', 
                header = {
                    'workdir' : pathlib.Path(tmp_fd / 'workdir')
                }
            )
            buffer = ErrorBuffer(lock_file)
            buffer.add_entry("Error", "Error", "WARNING")
            with open(buffer.file_path, 'r') as f:
                content = json.load(f)
                error = content['errors'][0]
                self.assertEqual(content, buffer.serialize())
                self.assertEqual(content['errors'][0]['type'], 'WARNING')
                self.assertEqual(error['title'], 'Error')
                self.assertEqual(error['content'], 'Error')