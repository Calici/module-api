import unittest
import pathlib

from .field import ListField, LockField
from .section import LockSection
from .file import LockIO
from .calici import LockHeader, LockStatus
from API.lock.fields.list import ListField as ListFields, Lock, Generic
from API.lock.fields.list import TupleField as TupleFields

class TestField(unittest.TestCase):
    def test_initialize(self):
        field   = LockField(float)
        self.assertEqual(field._type, float)

    def test_initialize_with_default(self):
        field   = LockField(float, default = 0.0)
        self.assertEqual(field._changed, False)

    def test_initialize_and_set_value(self):
        field   = LockField(float)
        field.set(0.0)
        self.assertEqual(field._changed, True)
        self.assertEqual(field.get(), 0.0)

    def test_serializer(self):
        field   = LockField(pathlib.Path)
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
        self.assertEqual(field, field2)

class TestListField(unittest.TestCase):
    def test_init_no_default_then_set_value(self):
        field   = ListField(child = LockField(str))
        truth   = ['asdf', 'asfs']
        field.set(truth)
        cur     = field.get()
        self.assertEqual(
            all([cur[i] == truth[i] for i in range(len(truth))]), True
        )
        self.assertEqual(
            field.changed(), True
        )

    def test_init_with_default(self):
        truth   = ['asdf', 'afds', 'dfsdf']
        field   = ListField(LockField(str), truth)
        cur     = field.get()
        self.assertEqual(
            all([cur[i] == truth[i] for i in range(len(truth))]), True
        )
        self.assertEqual(
            field.changed(), False
        )
    
    def test_broken_type(self):
        truth   = [0, 1, 2, 32]
        field   = ListField(LockField(int), truth)
        try:
            field.set(['asdf', 'asdf', 'asdf'])
        except TypeError: return
        self.assertEqual(False, True)

    def test_max_length_with_default(self):
        truth   = ['asdf', 'adsf', 'aaaa']
        field   = ListField(LockField(str), truth, 2)
        self.assertEqual(field.get().__len__(), 2)
    
    def test_max_length_without_default(self):
        truth   = ['adff', 'aaaa', 'bbbb']
        field   = ListField(LockField(str), max_length = 2)
        self.assertEqual(field.get().__len__(), 0)
        field.set(truth)
        self.assertEqual(field.get().__len__(), 2)

class TestSection(unittest.TestCase):
    def test_init_section(self):
        class LockSectionTest(LockSection):
            test_number = LockField(int, default = 0)
            test_count  = LockField(int, default = 0)
            test_name   = LockField(str, default = 'lol')
            test_lol    = ListField(child = LockField(type = str), default = [])
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
        self.assertEqual(test.changed(), True)

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
        self.assertEqual(test.test_number, 1)
        self.assertEqual(test.test_count, 1)
    
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
        self.assertEqual(test.test_number, 1)
        self.assertEqual(test.test_count, 1)
        self.assertEqual(test.changed(), False)
        self.assertEqual(test.test_attr, {
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
        self.assertEqual(lock.status.status, 'INIT')
        self.assertEqual(lock.status.is_connected, True)

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
        self.assertEqual(lock_1.header.process, 'dock_lol')
        self.assertEqual(lock_2.status.status, 'INIT')
        self.assertEqual(lock_2.status.is_connected, True)

class ListLockField(unittest.TestCase):
    def test_append(self):
        truth = ["nur", "sul", "tan"]
        field = ListFields(Lock.LockField(str), truth)
        field.append("bek")
        self.assertEqual(field._buffer.__len__(), 1)
        self.assertEqual(field._buffer[0]["type"], "append")
        self.assertEqual(field._buffer[0]["elm"],"bek")
        self.assertEqual(len(truth), 4)
        self.assertEqual(truth[3], "bek")

    def test_reorder(self):
        field = ListFields(Lock.LockField(int))
        field._value = [1, 2, 3, 4, 5]
        field.reorder([4, 2, 0, 3, 1])
        self.assertEqual(field._buffer[0]["type"], "reorder")
        self.assertEqual(field._buffer[0]["newOrder"], [4, 2, 0, 3, 1])
        self.assertEqual(len(field._value), 5)
        self.assertEqual(field._value, [5, 3, 1, 4, 2])

    def test_modify(self):
        field = ListFields(Lock.LockField(float))
        field._value = [1.1, 2.2, 3.3, 4.4]
        field.modify(1, 5.5)
        self.assertEqual(field._buffer[0]["type"], "modify")
        self.assertEqual(field._buffer[0]["pos"], 1)
        self.assertEqual(field._buffer[0]["elm"], 5.5)
        self.assertEqual(len(field._value), 4)
        self.assertEqual(field._value, [1.1, 5.5, 3.3, 4.4])

    
    def test_remove(self):
        field = ListFields(Lock.LockField(str))
        field._value = ["KYR", "GYZS", "TAN"]
        field.remove(1)
        self.assertEqual(field._buffer[0]["type"], "remove")
        self.assertEqual(field._buffer[0]["pos"], 1)
        self.assertEqual(len(field._value), 2)
        self.assertEqual(field._value, ["KYR", "TAN"])

    def test_empty(self):
        field = ListFields(Lock.LockField(bool))
        field._value = [True, False, True]
        field.empty()
        self.assertEqual(field._buffer[0]["type"], "empty")
        self.assertEqual(len(field._value), 0)

    def test_flush(self):
        field = ListFields(Lock.LockField(int))
        field._buffer =  [{"type": "append", "elm": 1}, {"type": "remove", "pos": 0}]
        field.flush()
        self.assertEqual(field._buffer, [])

    if __name__ == '__main__':
        unittest.main()

class TupleField(unittest.TestCase):
    def test_modify(self):
        field = TupleFields([Lock.LockField(str), Lock.LockField(int)], length=2)
        field.set(("Nurs", 2003))
        field.modify(0, "KGZ")
        self.assertEqual(field.get(), ("KGZ", 2003))
        self.assertEqual(field.changed(), True)

    def test_flush(self):
        field = TupleFields([Lock.LockField(str), Lock.LockField(int)], length=2)
        field.set(('abc', 123))
        field.modify(0, 'def')
        field.flush()
        self.assertEqual(field.changed(), True)
    
    def test_modify_tuple(self):
        class TestSection(LockSection):
            a = LockField(str, default = "a")
        field = TupleFields([TestSection()], length=1)
        field.modify(0, {"a" : "IRT"})
        self.assertEqual(field._value, ({"a": "IRT"},))
        self.assertEqual(field.changed(), False)
    
    def test_flush_tuple(self):
        class TestSection(LockSection):
            a = LockField(str, default="a")
        field = TupleFields([TestSection()], length=1)
        field._buffer = [{"type":"modify", "pos": 0, "elm": {"a" : "IRT"}}]
        field.flush()
        self.assertEqual(field._buffer, [])
        self.assertEqual(field.changed(), False)

    def test_append_list(self):
        class TestSection(LockSection):
            b = LockField(str, default="b")
        field = ListFields(TestSection())
        try:
            field.append("soodon")
            self.assertEqual("true", "false")
        except ValueError:
            pass

    def test_reorder_list(self):
        class TestSection(LockSection):
            b = LockField(str, default="b")
        field = ListFields(TestSection())
        field._value = [{"b" : "A"}, {"b" : "C"}, {"b" : "G"}, {"b" : "T"}]
        field.reorder([3, 0, 2, 1])
        self.assertEqual(field._value, [{"b" : "T"}, {"b" : "A"}, {"b" : "G"}, {"b" : "C"}])
        self.assertEqual(field.changed(), False)
    
    def test_modify_list(self):
        class TestSection(LockSection):
            b = LockField(str, default="b")
        field = ListFields(TestSection())
        field._value = [{"b" : "A"}, {"b" : "C"}, {"b" : "G"}, {"b" : "T"}]
        try:
            field.modify(3, "C")
            self.assertEqual("true", "false")
        except:
            pass

    def test_remove_list(self):
        class TestSection(LockSection):
            b = LockField(str, default="b")
        field = ListFields(TestSection())
        field._value = [{"b" : "A"}, {"b" : "C"}, {"b" : "G"}, {"b" : "T"}]
        field.remove(2)
        self.assertEqual(field._value, [{"b" : "A"}, {"b" : "C"}, {"b" : "T"}])
        self.assertEqual(field.changed(), False)
    
    def test_empty_list(self):
        class TestSection(LockSection):
            b = LockField(str, default="b")
        field = ListFields(TestSection())
        field._value = [{"b" : "A"}, {"b" : "C"}, {"b" : "G"}, {"b" : "T"}]
        field.empty()
        self.assertEqual(field._value, [])
        self.assertEqual(field.changed(), False)
    
    def test_flush_list(self):
        class TestSection(LockSection):
            b = LockField(str, default="b")
        field = ListFields(TestSection())
        field._buffer = [{"type": "modify", "pos": 1, "elm": {"b":"G"}}, {"type": "append", "elm": {"b":"T"}}]
        field.flush()
        self.assertEqual(field._buffer, [])
        self.assertEqual(field.changed(), False)





    



        
        
