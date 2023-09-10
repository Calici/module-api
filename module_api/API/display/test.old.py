from .component import ComponentWithTable as AllAllowedComponent, ComponentWithTable
from .display import Display

import unittest
import pathlib
import API.lock as lock
import shutil
import json

class TestDisplay(unittest.TestCase):
    def setUp(self):
        test_folder     = pathlib.Path('./.temp').resolve()
        test_lock_file  = lock.CaliciLock(
            test_folder / 'calici.lock', 
            header = {'workdir' : test_folder}
        )
        test_lock_file.__init_display__()
        self.lock           = test_lock_file
        self.test_folder    = test_folder

    def test_init(self):
        display     = Display(
            lock = self.lock,
            dtype = 0,
            component = ComponentWithTable()
        )
        self.assertEqual(
            pathlib.Path(display.file_path).is_file(), True
        )
        self.assertEqual(
            pathlib.Path(display.file_path).is_file(), True
        )
        self.assertEqual(
            display.component.messages.__len__(), 0
        )
        with open(display.file_path) as f:
            cont    = json.load(f)
            self.assertEqual(
                cont['dtype'], 0
            )

    def test_init_and_set_values(self):
        display     = Display(
            lock    = self.lock, dtype = 0,
            component = ComponentWithTable()
        )
        messages    = display.component.messages
        messages.append('ASDF')
        display.component.set(
            progress = 0.0, messages = messages
        )
        display.save()
        with open(display.file_path, 'r') as f:
            content = f.read()
        self.assertEqual(
            content, json.dumps(display.serialize())
        )
    
    def test_display_functions(self):
        display     = Display(
            lock = self.lock, dtype = 1,
            component = ComponentWithTable()
        )
        display.status_complete()
        with open(display.file_path, 'r') as f:
            content     = json.load(f)
            self.assertEqual(
                content['component']['status'], lock.LockIOStatusType.COMPLETE
            )
    
    def test_dtype_functioning(self):
        display     = Display(
            lock = self.lock, dtype = 1, 
            component = ComponentWithTable()
        )
        display.status_complete()
        with open(display.file_path, 'r') as f:
            content     = json.load(f)
            self.assertEqual(content['dtype'], 1)

    def test_table_types_sortable_and_zoomable(self):
        display     = Display(
            lock = self.lock, dtype = 0, component = ComponentWithTable(
                table = {
                    'types' : [
                        {'type' : 'number', 'sortable' : True}, 
                        {'type' : 'number', 'zoomable' : True}
                    ]
                }
            )
        )
        display2    = Display(
            lock = self.lock, dtype = -1, component = AllAllowedComponent()
        )
        display2.set(**display.serialize())
        self.assertEqual(
            display2.component.table.types[0]['type'], 'number'
        )
        self.assertEqual(
            display2.component.table.types[0]['sortable'], True
        )
        self.assertEqual(
            display2.component.table.types[0]['zoomable'], False
        )
        self.assertEqual(
            display2.component.table.types[1]['type'], 'number'
        )
        self.assertEqual(
            display2.component.table.types[1]['sortable'], False
        )
        self.assertEqual(
            display2.component.table.types[1]['zoomable'], True
        )
    def test_table_types_zoomable(self):
        display     = Display(
            lock = self.lock, dtype = 0, component = ComponentWithTable(
                table = {
                    'types' : [{'type' : 'number', 'zoomable' : True}]
                }
            )
        )
        display2    = Display(
            lock = self.lock, dtype = -1, component = AllAllowedComponent()
        )
        display2.set(**display.serialize())
        self.assertEqual(
            display2.component.table.types[0]['type'], 'number'
        )
        self.assertEqual(
            display2.component.table.types[0]['sortable'], False
        )
        self.assertEqual(
            display2.component.table.types[0]['zoomable'], True
        )

    def tearDown(self):
        shutil.rmtree(
            self.test_folder
        )