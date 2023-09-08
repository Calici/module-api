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

import unittest
import pathlib
import API.lock as lock
import shutil
import json

class TestDisplay(unittest.TestCase):
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
                    ], [
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