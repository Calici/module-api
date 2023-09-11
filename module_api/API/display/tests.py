from .display import Display
from .components import \
    v1_ComponentWithoutTable, \
    v1_ComponentWithTable, \
    v0_ComponentWithoutTable, \
    v0_ComponentWithTable
from .components.v1_table import \
    MutableTable as v1_MutableTable, \
    Header as v1_Header, \
    RowListField as v1_Rows, \
    TableType_ZoomableSortableI as v1_ZoomableSortable
from .components.v0_table import \
    v0_MutableTable, \
    ComponentWithTable as v0_ComponentWithTable
from .components.v0_no_table import \
    ComponentWithoutTable as v0_ComponentWithoutTable

import unittest
import pathlib
import module_api.API.lock as lock
import shutil
import json

class TestDisplay_v1(unittest.TestCase):
    def setUp(self):
        test_folder     = pathlib.Path('./.temp').resolve()
        test_folder.mkdir(parents = True, exist_ok = True)
        test_lock_file  = lock.CaliciLock(
            test_folder / 'calici.lock', 
            header = {'workdir' : test_folder}
        )
        test_lock_file.__init_display__()
        self.lock           = test_lock_file
        self.test_folder    = test_folder
    def tearDown(self):
        shutil.rmtree(
            self.test_folder
        )
    def test_init(self):
        display = Display(
            lock = self.lock, dtype = 0, component = v1_ComponentWithoutTable()
        )
        self.assertEqual(pathlib.Path(display.file_path).is_file(), True)
        self.assertEqual(pathlib.Path(display.file_path).is_file(), True)
        self.assertEqual(len(display.component.messages), 0)
        with open(display.file_path) as f:
            self.assertEqual(json.load(f)['dtype'], 0)
    def test_init_and_set_values(self):
        display = Display(
            lock = self.lock, dtype = 0, component = v1_ComponentWithoutTable()
        )
        display.component.messages.append({
            "title" : "Hey", "content" : "Heyyy"
        })
        display.component.set(progress = {'value' : 0})
        display.save()
        with open(display.file_path, 'r') as f:
            content = f.read()
        self.assertEqual(content, json.dumps(display.serialize()))
        self.assertEqual(
            json.loads(content)["component"]["messages"][0], 
            {"title" : "Hey", "content" : "Heyyy"}
        )
    def test_display_functions(self):
        display = Display(
            lock = self.lock, dtype = 0, component = v1_ComponentWithoutTable()
        )
        display.status_complete()
        with open(display.file_path, 'r') as f:
            content     = json.load(f)
            self.assertEqual(
                content['component']['status'], lock.LockIOStatusType.COMPLETE
            )
    def test_component_with_table(self):
        display = Display(
            lock = self.lock, dtype = 1, 
            component = v1_ComponentWithTable(
                v1_MutableTable(
                    v1_Header.create_header([{
                        'displayName' : 'Column 1', 
                        'type' : v1_ZoomableSortable()
                    }, {
                        'displayName' : 'Column 2', 
                        'type' : v1_ZoomableSortable()
                    }]),
                    v1_Rows([
                        lock.TypeField(lock.LockField, str), 
                        lock.TypeField(lock.LockField, str)
                    ], 
                    default = [
                        ["1.1", "1.2"], ["2.1", "2.2"]
                    ])
                    
                )
            )
        )
        rows = display.component.table.rows.get()
        for i in range(len(rows)):
            row = rows[i].get()
            for j in range(len(row)):
                cell = row[j].get()
                self.assertEqual(cell, '{0}.{1}'.format(i + 1, j + 1))
        display.save()
        with open(display.file_path, 'r') as f:
            content = f.read()
            self.assertEqual(content, json.dumps(display.serialize()))
            content = json.loads(content)
            self.assertEqual(
                len(content['component']['table']['rows']), 2
            )
            rows = content['component']['table']['rows']
            self.assertEqual(rows[0], ["1.1", "1.2"])
            self.assertEqual(rows[1], ["2.1", "2.2"])

class TestDisplay_v0(unittest.TestCase):
    def setUp(self):
        test_folder     = pathlib.Path('./.temp').resolve()
        test_folder.mkdir(parents = True, exist_ok = True)
        test_lock_file  = lock.CaliciLock(
            test_folder / 'calici.lock', 
            header = {'workdir' : test_folder}
        )
        test_lock_file.__init_display__()
        self.lock           = test_lock_file
        self.test_folder    = test_folder
    def tearDown(self):
        shutil.rmtree(
            self.test_folder
        )
    def test_init_display_no_table_v0(self):
        display = Display(self.lock, v0_ComponentWithoutTable())
        self.assertEqual(pathlib.Path(display.file_path).is_file(), True)
        self.assertEqual(pathlib.Path(display.file_path).is_file(), True)
        self.assertEqual(len(display.component.messages), 0)
        with open(display.file_path) as f:
            self.assertEqual(json.load(f)['dtype'], 0)
    def test_add_log_message_no_table_v0(self):
        display = Display(self.lock, v0_ComponentWithoutTable())
        display.component.messages.append(
            {"title" : "A New Title", "content" : "Yay"}
        )
        self.assertEqual(len(display.component.messages), 1)
        display.save()
        with open(display.file_path, 'r') as f:
            content = f.read()
            self.assertEqual(content, json.dumps(display.serialize()))
            self.assertEqual(
                json.loads(content)['component']['messages'][0], 
                {'title' : "A New Title", "content" : "Yay"}
            )