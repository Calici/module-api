# -*- coding: utf-8 -*-
"""File tool function
"""

from types import GeneratorType
from enum import Enum
from pathlib import Path, _make_selector
from typing import Union, List, Dict
import fnmatch
import logging
import json
import os
import shutil
import datetime as dt
import zipfile


def is_blank_str(my_string: str) -> bool:
    """Check string is empty or blank
    Args:
        my_string (str): Description

    Returns:
        bool: False if my_string empty or contains spaces only
    """
    return isinstance(my_string, str) and not (my_string and my_string.strip())

def is_list(l) -> bool:
    """Check l is list or not

    Args:
        l (list)

    Returns:
        bool
    """
    return isinstance(l, list)

class FileEncoding:
    """File Encoding
    """
    # https://docs.python.org/3.8/library/codecs.html#standard-encodings
    UTF_7 = "utf-7"  # encodings.utf_7.getregentry().name
    UTF_8 = "utf-8"  # encodings.utf_8.getregentry().name or cp65001
    UTF_8_BOM = "utf-8-sig"  # encodings.utf_8_sig.getregentry().name
    UTF_16 = "utf-16"  # encodings.utf_16.getregentry().name
    UTF16_LE = "utf-16-le"  # encodings.utf_16_le.getregentry().name
    UTF16_BE = "utf-16-be"  # encodings.utf_16_be.getregentry().name
    UTF32_LE = "utf-32-le"  # encodings.utf_32_le.getregentry().name
    UTF32_BE = "utf-32-be"  # encodings.utf_32_be.getregentry().name
    UTF_32 = "utf-32"  # encodings.utf_32.getregentry().name
    SHIFT_JIS = "shift_jis"  # encodings.shift_jis.getregentry().name
    VIETNAMESE = "cp1258"  # encodings.cp1258.getregentry().name


class UniversalEncoder(json.JSONEncoder):
    """Json encodes object

    Args:
        json (_type_): _description_

    Returns:
        _type_: _description_
    """
    ENCODER_BY_TYPE = {
        dt.datetime: lambda o: o.isoformat(),
        dt.date: lambda o: o.isoformat(),
        dt.time: lambda o: o.isoformat(),
        set: list,
        frozenset: list,
        GeneratorType: list,
        bytes: lambda o: o.decode(),
    }

    def default(self, o):
        if isinstance(o, Enum):
            return o.value
        for k, v in self.ENCODER_BY_TYPE.items():
            if isinstance(o, k):
                encoder = v
                return encoder(o)

        if (o.__class__.__module__ + "." + o.__class__.__name__) == "pydantic.main.BaseModel":
            return o.dict()

        if "file_lib.PathEx" in (o.__class__.__module__ + "." + o.__class__.__name__):
            return {'path': str(self)}

        try:
            return super().default(o)
        except TypeError:
            try:
                return o.__dict__
            except AttributeError:
                return str(o)


class PathEx(Path):
    """Extend of pathlib.Path
    """
    _flavour = Path()._flavour

    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls, *args, **kwargs)
        return self

    def check_existed(self, b_existed: bool = True):
        """Check item exists or not

        Args:
            b_existed:(bool, optional): Defaults to True.
                True: raise FileNotFoundError if file is not exists
                False: raise FileExistsError if file exists

        Raises:
            FileNotFoundError
            FileExistsError
        """
        if b_existed:
            if not self.exists():
                raise FileNotFoundError(f"{self} does not exist")
        else:
            if self.exists():
                raise FileExistsError(f"{self} is existed")

    def check_folder(self):
        """Check self is folder or not

        Raises:
            NotADirectoryError: not a folder
        """
        self.check_existed()
        if not self.is_dir():
            raise NotADirectoryError(f"{self} is not folder")

    def is_empty_folder(self) -> bool:
        """Check self is folder or not

        Raises:
            NotADirectoryError: not a folder
        """
        self.check_folder()
        data = self.glob('*')
        try:
            next(data)
        except StopIteration:
            return True

        return False

    def check_file(self):
        """Check self is file or not

        Raises:
            FileNotFoundError: not a file
        """
        self.check_existed()
        if not self.is_file():
            raise FileNotFoundError(f"{self} is not file")

    def __ex_glob_folder(
        self,
        pattern: str,
        is_folder: bool = False,
        is_file: bool = False,
        exclude_names: Union[List[str], None] = None,
        is_exclude_names_case: bool = True
    ):
        """_summary_

        Args:
            pattern (str, optional): Defaults to '*'.
            is_folder (bool, optional): return folders in result. Defaults to False.
            is_file (bool, optional): return files in result. Defaults to False.
            exclude_names (List[str], optional): ['*a.html', '???']. Defaults to None.
            is_exclude_names_case (bool, optional): Case sensitive on match exclude names.
                Defaults to True.

        Returns:
            _type_: _description_
        """
        ret: List[PathEx] = []
        if exclude_names is None:
            exclude_names = []
        compare_func = fnmatch.fnmatchcase if is_exclude_names_case else fnmatch.fnmatch
        for item in self.glob(pattern):
            b_match = False
            for ex_name in exclude_names:
                relative_path = item.relative_to(self)
                if compare_func(str(relative_path), ex_name):
                    b_match = True
                    break
            if not b_match:
                if is_folder and item.is_dir():
                    ret.append(item)
                if is_file and item.is_file():
                    ret.append(item)
        return ret

    @staticmethod
    def get_current_dir(path: Union[Path, str]):
        """Get current dir of path

        Args:
            path (Path | str): source path

        Returns:
            PathEx
        """
        return PathEx(path).parent.resolve()

    def mkdir_ex(self, mode: int = 511, force_delete: bool = False):
        """Create folder
            Args:
                mode: mode of folder
                force_delete: will delete folder if it already exists
        """
        if force_delete and self.exists():
            self.remove()
        self.mkdir(mode=mode, parents=True, exist_ok=True)

    def symlink_rel_to(self, target: Union[Path, str]):
        """Create a symlink pointing to ``target`` from ``location``.
        Args:
            symlink: The location of the symlink itself.
            destination: The target of the symlink (the file/directory that is pointed to)
        """

        target = PathEx(target).resolve()
        self.symlink_to(os.path.relpath(target, self.parent.resolve()), target_is_directory=target.is_dir())

    def size(self, unit: str = 'bytes') -> float | int:
        """Get folder size in unit

        Args:
            unit (str, optional): ['bytes', 'KB', 'MB', 'GB']. Defaults to 'bytes'.

        Returns:
            float | int: size of folder in unit
        """
        self.check_existed(b_existed=True)
        total_size = 0
        if self.is_file():
            total_size = self.stat().st_size
        elif self.is_dir():
            folder_path = str(self)
            list_units = ['bytes', 'KB', 'MB', 'GB']
            if unit not in list_units:
                unit = 'bytes'
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(filepath)
        else:
            return 0
        if unit == 'KB':
            return total_size / 1_024.0
        elif unit == 'MB':
            return total_size / 1_024.0 / 1_024.0
        elif unit == 'GB':
            return total_size / 1_024.0 / 1_024.0 / 1_024.0
        else:
            return total_size

    def copy_to(
        self,
        dest: Union[Path, str],
        b_overwrite: bool = True,
        ignore_types: Union[List[str], None] = None,
        include_types: Union[List[str], None] = None,
        ignore_folder: Union[List[str], None] = None,
        b_recursive: bool = True
    ):
        """Copy src/* to dest/*

        Args:
            dest (_type_): _description_
            b_overwrite (bool, optional): Overwrite?. Defaults to True.
            ignore_types (list, optional): Ignore types. Example: ['chm','html']. Defaults to None.
            include_types (list, optional): Include types. Example: ['chm','html'].
                Defaults to None.
            ignore_folder (list, optional): Ignore folders. Example: folder1. Defaults to None.
            b_recursive (bool, optional): Copy subfolder's contents.. Defaults to True.

        Raises:
            RuntimeError: _description_
        """
        src = self
        dest = PathEx(dest)

        if src.is_symlink():
            return
        if src.is_file():
            shutil.copy(src, dest)
            return

        src.check_folder()
        dest.mkdir_ex()
        for f in src.glob('*'):
            if f.is_dir():
                if ignore_folder and f.name in ignore_folder:
                    continue
                if b_recursive:
                    f.copy_to(
                        dest / f.name,
                        b_overwrite=b_overwrite,
                        ignore_types=ignore_types,
                        include_types=include_types,
                        ignore_folder=ignore_folder,
                        b_recursive=b_recursive
                    )
                else:
                    (dest / f.name).mkdir_ex()
            else:
                file_type = f.suffix.lstrip('.')
                if ignore_types and file_type in ignore_types:
                    continue
                if not b_overwrite and (dest / f.name).exists():
                    continue
                if (include_types and file_type in include_types) or not include_types:
                    shutil.copy(f, dest)

    def count_child_files(self, file_type: str = '*', b_recursive: bool = False) -> int:
        """
        count files in one folders
        """
        self.check_folder()
        l = self.list_files(f'*.{file_type}', level=0)
        ret = len(l)

        if b_recursive:
            for _ in self.list_sub_folders('*', level=-1):
                ret += _.count_child_files(file_type=file_type, b_recursive=False)
        return ret

    def move_children_to(self, dest_folder: Union[Path, str]):
        """Move all children to dest_folder

        Args:
            dest_folder (Union[Path, str]): _description_
        """
        self.check_folder()
        dest_folder = PathEx(dest_folder)
        dest_folder.mkdir_ex()
        for _ in self.glob('*'):
            shutil.move(_, dest_folder / _.name)

    def is_binary_file(self):
        """Return true if the given filename is binary.

        Raises an EnvironmentError if the file does not exist or cannot be
        accessed.
        """
        self.check_existed(True)
        if not self.is_file():
            raise FileNotFoundError(f"{self} is not a file")

        fin = open(self, "rb")
        ret = False
        try:
            chunk_size = 1024
            while True:
                chunk = fin.read(chunk_size)
                if 0 in chunk:  # found null byte
                    ret = True
                    break
                if len(chunk) < chunk_size:
                    break  # done
        finally:
            fin.close()

        return ret

    def list_sub_folders(
        self,
        pattern: str = '*',
        level: int = 0,
        b_print: bool = False,
        b_log: bool = False,
        b_only_leaf_folder: bool = False,
        exclude_names: Union[List[str], None] = None,
        is_exclude_names_case: bool = True
    ):
        """List child folders of parent folder

        Args:
            pattern (str, optional): Defaults to '*'.
            level:
                -1: no limit
                0: current folder
            b_print (bool, optional): Show folder path on screen. Defaults to False.
            b_log (bool, optional): Show folder path on logging. Defaults to False.
            b_only_leaf_folder (bool, optional): Only show folders have in level=0.
                Defaults to False.
            exclude_names (List[str], optional): ['*a.html', '???']. Defaults to None.
            is_exclude_names_case (bool, optional): Case sensitive on match exclude names.
                Defaults to True.

        Returns:
            List[Path]: list of folders' path
        """
        if b_print:
            print(self)
        if b_log:
            logging.info(str(self))

        if level < 0:
            level = -1
        if '/' in pattern:
            raise ValueError('Pattern must not include /')
        self.check_folder()
        ret = []
        if level == -1:
            return self.__ex_glob_folder(
                pattern=f'**/{pattern}',
                is_folder=True,
                exclude_names=exclude_names,
                is_exclude_names_case=is_exclude_names_case
            )

        if b_only_leaf_folder and level == 0:
            return self.__ex_glob_folder(
                pattern=pattern,
                is_folder=True,
                exclude_names=exclude_names,
                is_exclude_names_case=is_exclude_names_case
            )
        elif not b_only_leaf_folder:
            ret = self.__ex_glob_folder(
                pattern=pattern,
                is_folder=True,
                exclude_names=exclude_names,
                is_exclude_names_case=is_exclude_names_case
            )

        if level > 0:
            folders = self.__ex_glob_folder(
                pattern='*', is_folder=True, exclude_names=exclude_names, is_exclude_names_case=is_exclude_names_case
            )
            for _ in folders:
                ret.extend(
                    _.list_sub_folders(
                        pattern=pattern,
                        level=level - 1,
                        b_print=b_print,
                        b_log=b_log,
                        b_only_leaf_folder=b_only_leaf_folder,
                        exclude_names=exclude_names,
                        is_exclude_names_case=is_exclude_names_case
                    )
                )

        return ret

    def list_sub_folders_str(
        self,
        pattern: str = '*',
        level: int = 0,
        b_print: bool = False,
        b_log: bool = False,
        b_only_leaf_folder: bool = False,
        exclude_names: Union[List[str], None] = None,
        is_exclude_names_case: bool = True
    ) -> List[str]:
        """List child folders of parent folder

        Args:
            pattern (str, optional): Defaults to '*'.
            level:
                -1: no limit
                0: current folder
            b_print (bool, optional): _description_. Defaults to False.
            b_log (bool, optional): _description_. Defaults to False.
            b_only_leaf_folder (bool, optional): Only show folders have in level=0.
                Defaults to False.
            exclude_names (List[str], optional): ['*a.html', '???']. Defaults to None.
            is_exclude_names_case (bool, optional): Case sensitive on match exclude names.
                Defaults to True.

        Returns:
            List[str]: _description_
        """
        ret = self.list_sub_folders(
            pattern,
            level,
            b_print=b_print,
            b_log=b_log,
            b_only_leaf_folder=b_only_leaf_folder,
            exclude_names=exclude_names,
            is_exclude_names_case=is_exclude_names_case
        )
        ret = [str(f) for f in ret]
        return ret

    def list_files(
        self,
        pattern: str = '*',
        level: int = 0,
        b_print: bool = False,
        b_log: bool = False,
        b_only_leaf_folder: bool = False,
        exclude_names: Union[List[str], None] = None,
        is_exclude_names_case: bool = True
    ):
        """List child files of parent folder

        Args:
            pattern (str, optional): Defaults to '*'.
            level:
                -1: no limit
                0: current folder
            b_print (bool, optional): Show folder path on screen. Defaults to False.
            b_log (bool, optional): Show folder path on logging. Defaults to False.
            b_only_leaf_folder (bool, optional): Only show files have in level=0.
                Defaults to False.
            exclude_names (List[str], optional): ['*a.html', '???']. Defaults to None.
            is_exclude_names_case (bool, optional): Case sensitive on match exclude names.
                Defaults to True.

        Returns:
            List[Path]: list of files' path
        """

        if '/' in pattern:
            raise ValueError('Pattern must not include /')
        self.check_folder()
        if b_print:
            print(self)
        if b_log:
            logging.info(str(self))

        if level < 0:
            level = -1
        self.check_folder()
        ret = []
        if level == -1:
            return self.__ex_glob_folder(
                pattern=f'**/{pattern}',
                is_file=True,
                exclude_names=exclude_names,
                is_exclude_names_case=is_exclude_names_case
            )

        if b_only_leaf_folder and level == 0:
            return self.__ex_glob_folder(
                pattern=pattern, is_file=True, exclude_names=exclude_names, is_exclude_names_case=is_exclude_names_case
            )
        elif not b_only_leaf_folder:
            ret = self.__ex_glob_folder(
                pattern=pattern, is_file=True, exclude_names=exclude_names, is_exclude_names_case=is_exclude_names_case
            )

        if level > 0:
            folders = self.__ex_glob_folder(
                pattern='*', is_folder=True, exclude_names=exclude_names, is_exclude_names_case=is_exclude_names_case
            )
            for _ in folders:
                ret.extend(
                    _.list_files(
                        pattern=pattern,
                        level=level - 1,
                        b_print=b_print,
                        b_log=b_log,
                        b_only_leaf_folder=b_only_leaf_folder,
                        exclude_names=exclude_names,
                        is_exclude_names_case=is_exclude_names_case
                    )
                )

        return ret

    def list_files_str(
        self,
        pattern: str = '*',
        level: int = 0,
        b_print: bool = False,
        b_log: bool = False,
        b_only_leaf_folder: bool = False,
        exclude_names: Union[List[str], None] = None,
        is_exclude_names_case: bool = True
    ) -> List[str]:
        """List child files of parent folder

        Args:
            pattern (str, optional): _description_. Defaults to '*'.
            level (int, optional): _description_. Defaults to 0.
            b_print (bool, optional): _description_. Defaults to False.
            b_log (bool, optional): _description_. Defaults to False.
            b_only_leaf_folder (bool, optional): Only show files have in level=0. Defaults to False.
            exclude_names (List[str], optional): ['*a.html', '???']. Defaults to None.
            is_exclude_names_case (bool, optional): Case sensitive on match exclude names.
                Defaults to True.

        Returns:
            List[str]: _description_
        """
        ret = self.list_files(
            pattern=pattern,
            level=level,
            b_print=b_print,
            b_log=b_log,
            b_only_leaf_folder=b_only_leaf_folder,
            exclude_names=exclude_names,
            is_exclude_names_case=is_exclude_names_case
        )
        ret = [str(f) for f in ret]
        return ret

    def load_file_to_str(
        self, encoding: str = FileEncoding.UTF_8, errors: str = "ignore", b_rstrip: bool = True
    ) -> str:
        """_summary_

        Args:
            encoding (str, optional): Defaults to FileEncoding.UTF_8.
            errors (str, optional): Defaults to "ignore".
            b_rstrip (bool, optional): Defaults to "True". Right strip space, \r, \n
        Returns:
            str: data of file
        """
        self.check_file()

        with open(self, "r", encoding=encoding, errors=errors) as f_source:
            s = f_source.read()
        if b_rstrip:
            s = s.rstrip(" \r\n")

        # remove encode character of BOM
        if s and s.startswith("\ufeff"):
            s = s[1:]

        return s

    def load_file_to_list_str_n_head(
        self,
        b_remove_blank_str: bool = False,
        encoding: str = FileEncoding.UTF_8,
        errors: str = "ignore",
        row_num: int = 10
    ) -> List[str]:
        """Load text unicode file to list(string)

        Args:
            encoding (str): default FileEncoding.UTF_8 (FileEncoding.UTF_8_BOM)
        Returns:
            List[str]: list of string containt file's content
        """
        self.check_file()

        lines: List[str] = []
        n = 0
        with open(self, "r", encoding=encoding, errors=errors) as f_source:
            while n < row_num:
                line = f_source.readline()
                if len(line) == 0:
                    break
                line = line.rstrip("\r\n")
                if not b_remove_blank_str or not is_blank_str(line):
                    n += 1
                    lines.append(line)

        # remove encode character of BOM
        if lines and lines[0].startswith("\ufeff"):
            lines[0] = lines[0][1:]

        return lines

    def load_file_to_list_str(
        self,
        b_remove_blank_str: bool = False,
        encoding: str = FileEncoding.UTF_8,
        errors: str = "ignore"
    ) -> List[str]:
        """Load text unicode file to list(string)

        Args:
            encoding (str): default FileEncoding.UTF_8 (FileEncoding.UTF_8_BOM)
        Returns:
            List[str]: list of string containt file's content
        """
        self.check_file()

        with open(self, "r", encoding=encoding, errors=errors) as f_source:
            lines = f_source.readlines()

        lines = [
            x.rstrip("\r\n") for x in lines if (b_remove_blank_str and not is_blank_str(x)) or not b_remove_blank_str
        ]

        # remove encode character of BOM
        if lines and lines[0].startswith("\ufeff"):
            lines[0] = lines[0][1:]

        return lines

    def write_str_to_file(
        self, data: str, encoding: str = FileEncoding.UTF_8, newline: str = "\n", mode: Union[int, None] = None
    ):
        """Write string data to text unicode file

        Args:
            encoding (str): default FileEncoding.UTF_8 (FileEncoding.UTF_8_BOM)
            newline (str): None, '', '\\n', '\\r', and '\\r\\n'
        """
        self.parent.mkdir_ex()
        if is_blank_str(data):
            raise ValueError("data is not empty")

        with open(self, "w+", encoding=encoding, newline=newline) as f_dest:
            f_dest.write(data)

        if mode is not None and mode != self.stat().st_mode:
            try:
                self.chmod(mode)
            except Exception:
                pass

    def write_list_str_to_file(
        self,
        data: List[str],
        b_remove_blank_str: bool = False,
        newline: str = "\n",
        encoding: str = FileEncoding.UTF_8,
        mode: Union[int, None] = None
    ):
        """Write list of string to unicode file

        Args:
            encoding (str): default FileEncoding.UTF_8 (FileEncoding.UTF_8_BOM)
            newline (str): None, '', '\\n', '\\r', and '\\r\\n'
        """
        self.parent.mkdir_ex()
        if not is_list(data):
            raise ValueError("data must be list(str)")

        new_data: List[str] = []
        for item in data:
            if b_remove_blank_str and is_blank_str(item):
                continue
            if item.endswith(newline):
                new_data.append(item)
            else:
                new_data.append(item + newline)

        # remove last blank line
        if new_data:
            new_data[-1] = new_data[-1].rstrip("\r\n")

        with open(self, "w+", newline=newline, encoding=encoding) as f_dest:
            f_dest.writelines(new_data)

        if mode is not None and mode != self.stat().st_mode:
            try:
                self.chmod(mode)
            except Exception:
                pass

    def append_str_to_file(self, data: str, encoding: str = FileEncoding.UTF_8, lock=None):
        """Append string data to end of unicode file

        Args:
            file_path (str): path of source file
            data (str): data
            encoding (str): default FileEncoding.UTF_8 (FileEncoding.UTF_8_BOM)
            lock: using when running thread
        """

        self.parent.mkdir_ex()
        if is_blank_str(data):
            raise ValueError("data is not empty")

        if lock is not None:
            # acquire the lock
            lock.acquire()

        with open(self, "a", encoding=encoding) as f_dest:
            f_dest.write(data)

        if lock is not None:
            # acquire the lock
            lock.release()

    def append_list_str_to_file(
        self,
        data: List[str],
        b_remove_blank_str: bool = False,
        newline: str = "\n",
        encoding: str = FileEncoding.UTF_8,
        lock=None
    ):
        """Append string data to end of unicode file

        Args:
            encoding (str): default FileEncoding.UTF_8 (FileEncoding.UTF_8_BOM)
            newline (str): None, '', '\\n', '\\r', and '\\r\\n'
            lock: using when running thread
        """
        self.parent.mkdir_ex()
        if not is_list(data):
            raise ValueError("data must be list(str)")

        n = len(data)
        if lock is not None:
            # acquire the lock
            lock.acquire()

        with open(self, "a", encoding=encoding, newline=newline) as f_dest:
            for i, item in enumerate(data):
                if b_remove_blank_str and is_blank_str(item):
                    continue

                if i < n - 1:
                    item = item.rstrip("\r\n") + newline

                # Remove \r \n in last line
                if i == n - 1:
                    item = item.rstrip("\r\n")

                if i == 0:
                    item = newline + item.lstrip("\r\n")

                f_dest.write(item)
        if lock is not None:
            # acquire the lock
            lock.release()

    def create_zip(self, dst: Union[Path, str], b_overwrite: bool = True):
        """Create a zip file

        Args:
            dst (Union[Path, str, None], optional): dest zip file. Defaults to None.
            b_overwrite (bool, optional): _description_. Defaults to True.

                    Raises:
            ValueError: _description_
            FileExistsError: _description_

        """
        dst = PathEx(dst)
        dst.parent.mkdir_ex()

        if dst.suffix != '.zip':
            dst = dst.with_suffix(".zip")

        if dst.exists() and b_overwrite:
            dst.unlink()
        elif dst.exists():
            raise FileExistsError(f"{dst} is exists")

        zf = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
        abs_src = os.path.abspath(self)
        for dirname, _, files in os.walk(self):
            for filename in files:
                absname = os.path.abspath(os.path.join(dirname, filename))
                arcname = absname[len(abs_src) + 1:]
                zf.write(absname, arcname)
        zf.close()
        return dst

    def extract_zip(self, dst: Union[Path, str, None] = None):
        """Create a zip file

        Args:
            dst : dest file
        """
        self.check_file()
        if dst is None:
            dst = self.parent / self.stem
        dst = PathEx(dst)
        dst.mkdir_ex()

        with zipfile.ZipFile(self, "r") as zip_ref:
            zip_ref.extractall(dst)

    def load_json_file(
        self,
        parse_float=None,
        parse_int=None,
        parse_constant=None,
        object_pairs_hook=None,
        encoding: str = FileEncoding.UTF_8
    ):
        """Load json data from file

        Returns:
            dict: json data

        """
        self.check_file()
        with open(self, "r", encoding=encoding) as f_source:
            json_data = json.load(
                f_source,
                parse_float=parse_float,
                parse_int=parse_int,
                parse_constant=parse_constant,
                object_pairs_hook=object_pairs_hook,
                # encoding=FileEncoding.UTF_8,    from python 3.9 not need
            )
        return json_data

    def write_dict_to_json_file(
        self,
        data: Union[List, Dict],
        encoding: str = FileEncoding.UTF_8,
        newline: str = "\n",
        indent: int = 2,
        mode: Union[int, None] = None
    ):
        """Write dict data to text file with json format

        Args:
            data (dict): dictionary data
            encoding (str):
            newline (str, optional): _description_. Defaults to "\n".
            indent (int, optional): _description_. Defaults to 2.
            mode (Union[int, None], optional): _description_. Defaults to None.
        """
        self.parent.mkdir_ex()

        with open(self, "w+", encoding=encoding, newline=newline) as f_dest:
            # Save direct to text file
            json.dump(data, f_dest, ensure_ascii=False, indent=indent, cls=UniversalEncoder)

        if mode is not None and mode != self.stat().st_mode:
            try:
                self.chmod(mode)
            except Exception:
                pass

    def write_dict_to_json_file_simple(
        self,
        data: Union[List, Dict],
        encoding: str = FileEncoding.UTF_8,
        newline: str = "\n",
        indent: int = -1,
        mode: Union[int, None] = None
    ):
        """Write dict data to text file with no format

        Args:
            file_path (str): dest file path
            data (dict, list): dictionary data
            encoding (str):
            newline (str, optional): _description_. Defaults to "\n".
            indent (int, optional): _description_. Defaults to 2.
            mode (Union[int, None], optional): _description_. Defaults to None.
        """
        self.parent.mkdir_ex()

        with open(self, "w+", encoding=encoding, newline=newline) as f_dest:
            # Save direct to text file
            if indent < 0:
                json.dump(data, f_dest, ensure_ascii=False)
            else:
                json.dump(data, f_dest, ensure_ascii=False, indent=indent)

        if mode is not None and mode != self.stat().st_mode:
            try:
                self.chmod(mode)
            except Exception:
                pass

    def remove(self):
        """Remove item
        """
        if self.is_dir():
            shutil.rmtree(self, ignore_errors=True)
        elif self.is_file() or self.is_symlink():
            self.unlink(missing_ok=True)

    def add_suffix(self, suffix: str):
        """Add suffix to file
        """
        suffix = suffix.lstrip('. ')
        return self.parent / (self.name + '.' + suffix)
