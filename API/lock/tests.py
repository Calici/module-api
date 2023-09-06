import unittest
import pathlib

from .field import  LockField
from .list import ListField
from .section import LockSection
from .file import LockIO
from .calici import LockHeader, LockStatus

class TestField(unittest.TestCase):
    def test_initialize(self):
        field   = LockField(float, 0.0)
        self.assertEqual(field.type, float)

    def test_initialize_with_default(self):
        field   = LockField(float, default = 0.0)
        self.assertEqual(field.is_changed(), False)

    def test_initialize_and_set_value(self):
        field   = LockField(float, 0.0)
        field.set(0.0)
        self.assertEqual(field.is_changed(), True)
        self.assertEqual(field.get(), 0.0)

    def test_serializer(self):
        field   = LockField(pathlib.Path, "")
        field.set(pathlib.Path('../lol'))
        self.assertEqual(isinstance(field.serialize(), str), True)
        self.assertEqual(isinstance(field.serialize_changes(), str), True)
        field.flush()
        self.assertEqual(field._changed, False)

    def test_one_cycle(self):
        field   = LockField(pathlib.Path, '../lol')
        field.set(pathlib.Path('../sdf'))
        field.serialize_changes()
        field.get()
        field.flush()

    def test_comparison(self):
        field   = LockField(pathlib.Path, '../lol')
        field2  = LockField(pathlib.Path, '../lol')
        self.assertEqual(field.get(), field2.get())

class TestSection(unittest.TestCase):
    def test_init_section(self):
        class LockSectionTest(LockSection):
            test_number = LockField(int, default = 0)
            test_count  = LockField(int, default = 0)
            test_name   = LockField(str, default = 'lol')
            test_lol    = ListField(
                child = LockField(str, ""), default = []
            )
        test    = LockSectionTest(
            test_number = 1, test_count = 1, test_name = 'abcd'
        )
        test_val= test.get()
        self.assertEqual(test_val['test_number'], 1)
        self.assertEqual(test_val['test_count'], 1)
        self.assertEqual(test_val['test_name'], 'abcd')
        self.assertEqual(test_val['test_lol'], [])
    def test_init_serialize(self):
        class LockSectionTest(LockSection):
            test_number = LockField(int, default = 0)
            test_count  = LockField(int, default = 0)
            test_name   = LockField(str, default = 'lol')
        test    = LockSectionTest(
            test_number = 1, test_count = 1, test_name = 'abcd'
        )
        test.set(test_name = 'asdfasdf')
        test_val= test.serialize()
        self.assertEqual(test_val['test_number'], 1)
        self.assertEqual(test_val['test_count'], 1)
        self.assertEqual(test_val['test_name'], 'asdfasdf')
        self.assertEqual(test.is_changed(), True)

    def test_init_serialize_changes(self):
        class LockSectionTest(LockSection):
            test_number = LockField(int, default = 0)
            test_count  = LockField(int, default = 0)
            test_name   = LockField(str, default = 'lol')
        test    = LockSectionTest(
            test_number = 1, test_count = 1, test_name = 'abcd'
        )
        test_val= test.serialize_changes()
        self.assertEqual(test_val, {})
    
    def test_get_value(self):
        class LockSectionTest(LockSection):
            test_number = LockField(int, default = 0)
            test_count  = LockField(int, default = 0)
            test_name   = LockField(str, default = 'lol')
        test    = LockSectionTest(
            test_number = 1, test_count = 1, test_name = 'abcd'
        )
        self.assertEqual(test.test_number.get(), 1)
        self.assertEqual(test.test_count.get(), 1)
    
    def test_recursive_set(self):
        class LockSectionBottom(LockSection):
            test_hah    = LockField(str, default = 'asdf')
        class LockSectionMid(LockSection):
            test_lol    = LockField(str, default = 'adsf')
            test_bot    = LockSectionBottom()
        class LockSectionTop(LockSection):
            test_number = LockField(int, default = 0)
            test_count  = LockField(int, default = 0)
            test_attr   = LockSectionMid()
        test    = LockSectionTop()
        test.set(test_number = 1)
        test.set(test_count  = 1)
        test.test_attr.set(test_lol = 'adsf')
        test.set(test_attr = {'test_bot' : {'test_hah' : 'ffff'}})
        test.flush()
        self.assertEqual(test.test_number.get(), 1)
        self.assertEqual(test.test_count.get(), 1)
        self.assertEqual(test.is_changed(), False)
        self.assertEqual(test.test_attr.get(), {
            'test_lol' : 'adsf', 'test_bot' : {'test_hah' : 'ffff'}}
        )

class TestLockIO(LockIO):
    header  = LockHeader()
    status  = LockStatus()

class TestFile(unittest.TestCase):
    TEST_LOCK_FILE_PATH     = pathlib.Path('./.temp').resolve()
    def setUp(self):
        if not self.TEST_LOCK_FILE_PATH.exists(): 
            self.TEST_LOCK_FILE_PATH.mkdir()
        
    def tearDown(self):
        for f in self.TEST_LOCK_FILE_PATH.iterdir():
            f.unlink()
        self.TEST_LOCK_FILE_PATH.rmdir()
    
    def test_create_lock_file(self):
        lock_name   = 'test.lock'
        lock        = TestLockIO(self.TEST_LOCK_FILE_PATH / lock_name)
        # Assert that file exist
        self.assertEqual(lock.file_path.exists(), True)
    
    def test_create_and_set_content_read(self):
        lock_name   = 'test.lock'
        lock        = TestLockIO(self.TEST_LOCK_FILE_PATH / lock_name)
        # Set field values
        lock.status.set(status = 'INIT')
        lock.set(
            status = {'is_connected' : True}
        )
        # Assert that the file have changed
        lock        = TestLockIO(self.TEST_LOCK_FILE_PATH / lock_name)
        # Read lock
        self.assertEqual(lock.status.status.get(), 'INIT')
        self.assertEqual(lock.status.is_connected.get(), True)

    def test_set_illegal_content(self):
        lock_name   = 'test.lock'
        lock        = TestLockIO(self.TEST_LOCK_FILE_PATH / lock_name)
        try:
            lock.set(status = {'last_check' : 'asf'})
            self.assertEqual(isinstance(0, str), True)
        except TypeError:
            return
        assert "No type error" == '0'

    def test_double_saving(self):
        lock_name   = 'test.lock'
        lock_1      = TestLockIO(self.TEST_LOCK_FILE_PATH / lock_name)
        lock_2      = TestLockIO(lock_1.file_path)
        # Set field values
        lock_1.set(
            status = {'status' : 'INIT', 'is_connected' : True}
        )
        lock_2.set(
            header = {'process' : 'dock_lol'}
        )
        lock_1.reload()
        lock_2.reload()
        self.assertEqual(lock_1.header.process.get(), 'dock_lol')
        self.assertEqual(lock_2.status.status.get(), 'INIT')
        self.assertEqual(lock_2.status.is_connected.get(), True)

class TestListField(unittest.TestCase):
    def test_append(self):
        truth = ["nur", "sul", "tan"]
        field = ListField(LockField(str, ""), truth)
        field.append("bek")
        self.assertEqual(field._buffer.__len__(), 1)
        operation = field._buffer[0, "append"]
        self.assertEqual(operation["elm"],"bek")
        self.assertEqual(len(field.get()), 4)
        self.assertEqual(field.get()[3], "bek")

    def test_reorder(self):
        old_order = [1, 5, 3, 6]
        new_reordered = [3, 2, 0, 1]
        field = ListField(LockField(int, 0), old_order)
        field.reorder(new_reordered)
        self.assertEqual(field._buffer.__len__(), 1)
        operation = field._buffer[0, "reorder"]
        self.assertEqual(operation["newOrder"], [3, 2, 0, 1])
        self.assertEqual(field.get(), [6, 3, 1, 5])

    def test_modify(self):
        nums = [1, 4, 5, 6, 3]
        inx = 3
        new_elem = 10
        field = ListField(LockField(int, 0), nums)
        field.modify(inx, new_elem)
        self.assertEqual(field._buffer.__len__(), 1)
        operation = field._buffer[0, "modify"]
        self.assertEqual(operation["pos"], 3)
        self.assertEqual(operation["elm"], 10)
        self.assertEqual(len(field.get()), 5)
    
    def test_remove(self):
        truth = ["nur", "sul", "tan"]
        inx = 1
        field = ListField(LockField(str, ""), truth)
        field.remove(1)
        self.assertEqual(field._buffer.__len__(), 1)
        operation = field._buffer[0, "remove"]
        self.assertEqual(operation["pos"], inx)
        self.assertEqual(len(field.get()), 2)

    def test_empty(self):
        truth = ["nur", "sul", "tan"]
        field = ListField(LockField(str, ""), truth)
        field.empty()
        self.assertEqual(field._buffer.__len__(), 1)
        operation = field._buffer[0, "empty"]
        self.assertEqual(len(field.get()), 0)

    def test_flush(self):
        truth = ["nur", "sul", "tan"]
        field = ListField(LockField(str, ""), truth)
        field.clear_buffer()
        self.assertEqual(field._buffer.__len__(), 0)
    
    def test_init_no_default_then_set_value(self):
        field   = ListField(LockField(str, ""), [])
        truth   = ['asdf', 'asfs']
        field.set(truth)
        cur     = field.get()
        self.assertEqual(
            all([cur[i] == truth[i] for i in range(len(truth))]), True
        )
        self.assertEqual(field.is_changed(), True)

    def test_init_with_default(self):
        truth   = ['asdf', 'afds', 'dfsdf']
        field   = ListField(LockField(str, ""), truth)
        cur     = field.get()
        self.assertEqual(
            all([cur[i] == truth[i] for i in range(len(truth))]), True
        )
        self.assertEqual(field.is_changed(), False)
    
    def test_broken_type(self):
        truth   = [0, 1, 2, 32]
        field   = ListField(LockField(int, 0), truth)
        try:
            field.set(['asdf', 'asdf', 'asdf'])
        except TypeError: return
        self.assertEqual(False, True)

    def test_max_length_with_default(self):
        truth   = ['asdf', 'adsf', 'aaaa']
        field   = ListField(LockField(str, ""), truth, 2)
        self.assertEqual(field.get().__len__(), 2)
    
    def test_max_length_without_default(self):
        truth   = ['adff', 'aaaa', 'bbbb']
        field   = ListField(LockField(str, ""), [], max_length = 2)
        self.assertEqual(field.get().__len__(), 0)
        field.set(truth)
        self.assertEqual(field.get().__len__(), 2)











    



        
        
