from .error import ErrorBuffer
from module_api.API.test import generate_test_fd
from module_api.API.lock import CaliciLock
import unittest
import json

class TestError(unittest.TestCase):
    def test_dumping(self):
        with generate_test_fd() as tmp_fd:
            lock_file = CaliciLock(tmp_fd / 'default.lock')
            buffer = ErrorBuffer(lock_file)
            buffer.add_entry("Error", "Error")
            with open(buffer.file_path, 'r') as f:
                self.assertEqual(json.load(f), buffer.serialize())