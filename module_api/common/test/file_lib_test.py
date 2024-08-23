import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from file_lib import PathEx
from other_lib import random_string


class CommonFileTests(unittest.TestCase):
    def setUp(self):
        self.BASE_DIR = PathEx.get_current_dir(__file__)
        self.json_file = self.BASE_DIR / "test.json"
        self.txt_file = self.BASE_DIR / "test.txt"

    def tearDown(self):
        pass

    def test_file_exists(self):
        self.json_file.check_file()

    def test_folder_exists(self):
        self.BASE_DIR.check_folder()

    def test_exists(self):
        self.txt_file.check_existed(True)

    def test_not_exists(self):
        not_exists_file = self.BASE_DIR / 'not_exists.txt'
        not_exists_file.remove()
        not_exists_file.check_existed(False)


class ReadFileTests(unittest.TestCase):
    def setUp(self):
        self.BASE_DIR = PathEx.get_current_dir(__file__)
        self.json_file = self.BASE_DIR / "test.json"
        self.txt_file = self.BASE_DIR / "test.txt"

    def tearDown(self):
        pass

    def test_load_file_to_str_ok_1(self):
        data = self.txt_file.load_file_to_str()
        self.assertEqual(data[:3], "123")

    def test_load_file_to_list_str_ok_1(self):
        data = self.txt_file.load_file_to_list_str()
        self.assertEqual(data[0], "123")
        self.assertEqual(data[1], "1234")

    def test_load_json_file_ok_1(self):
        data = self.json_file.load_json_file()
        self.assertTrue(isinstance(data, dict))
        self.assertDictEqual(data, {"a": 1, "b": "123"})


class WriteFileTests(unittest.TestCase):
    def setUp(self):
        self.BASE_DIR = PathEx.get_current_dir(__file__)
        self.test_folder = self.BASE_DIR / random_string(10)
        self.test_file_1 = self.test_folder / f"{random_string(10)}.txt"
        self.test_file_2 = self.test_folder / f"{random_string(10)}.txt"
        self.json_file_1 = self.test_folder / f"{random_string(10)}.json"
        self.json_file_2 = self.test_folder / f"{random_string(10)}.json"

        self.test_data = """Line 1
Line 2
"""
        self.test_datas = ["Line 12", "Line 22"]
        self.json_data = {"a": "a", "b": 1}

        self.test_folder.mkdir_ex()

    def tearDown(self):
        self.test_folder.remove()

    def test_write_str_file_ok_1(self):
        self.test_file_1.write_str_to_file(self.test_data)
        data = self.test_file_1.load_file_to_list_str()
        self.assertEqual(data[0], "Line 1")
        self.assertEqual(data[1], "Line 2")

    def test_write_str_file_ok_2(self):
        self.test_file_2.write_str_to_file(self.test_data)
        data = self.test_file_2.load_file_to_list_str()
        self.assertEqual(data[0], "Line 1")
        self.assertEqual(data[1], "Line 2")

    def test_write_list_str_file_ok_1(self):
        self.test_file_1.write_list_str_to_file(self.test_datas)
        data = self.test_file_1.load_file_to_list_str()
        self.assertEqual(data[0], "Line 12")
        self.assertEqual(data[1], "Line 22")

    def test_write_list_str_file_ok_2(self):
        self.test_file_2.write_list_str_to_file(self.test_datas)
        data = self.test_file_2.load_file_to_list_str()
        self.assertEqual(data[0], "Line 12")
        self.assertEqual(data[1], "Line 22")

    def test_write_dict_to_json_file_ok_1(self):
        self.json_file_1.write_dict_to_json_file(self.json_data)
        data = self.json_file_1.load_json_file()
        self.assertTrue(isinstance(data, dict))
        self.assertDictEqual(data, {"a": "a", "b": 1})

    def test_write_dict_to_json_file_ok_2(self) -> None:
        self.json_file_2.write_dict_to_json_file(self.json_data)
        data = self.json_file_2.load_json_file()
        self.assertTrue(isinstance(data, dict))
        self.assertDictEqual(data, {"a": "a", "b": 1})


if __name__ == '__main__':
    unittest.main()