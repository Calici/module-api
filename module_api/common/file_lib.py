# -*- coding: utf-8 -*-
"""File tool function
"""

import json
import os
import shutil
import zipfile
from fnmatch import fnmatch
from pathlib import Path
from typing_extensions import Union, List
import logging
import datetime
from pydantic import BaseModel
from types import GeneratorType
from enum import Enum


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


def __convert_path(file_path: Union[Path, str], b_check_exists: bool = False, b_create_parent: bool = False) -> Path:
    # Convert str to Path
    if isinstance(file_path, str):
        file_path = file_path.strip()

    if not file_path:
        raise ValueError("file_path is not None or empty")

    file_path = Path(file_path)

    # Check exists
    if b_check_exists and not file_path.exists():
        raise FileNotFoundError(f"Path {file_path} does not exist")

    # Create parent folder
    if b_create_parent:
        file_path.parent.mkdir(exist_ok=True)

    return file_path


def list_sub_folders(folder: Union[Path, str], pattern: str = '*', level=-1) -> List[Path]:
    """List child folders of parent folder

    Args:
        folder (str):
        pattern (str, optional): Defaults to '*'.
        level:
            -1: no limit
            0: current folder

    Returns:
        List[Path]: list of folders' path
    """

    folders = [f for f in os.scandir(folder) if f.is_dir()]
    ret = [Path(f.path) for f in folders if fnmatch(f.name, pattern)]
    if (level == -1 or level > 0):
        new_level = (level - 1) if level > 0 else level
        for f in folders:
            ret.extend(list_sub_folders(f.path, pattern=pattern, level=new_level))

    return ret


def list_sub_folders_str(folder: Union[Path, str], pattern: str = '*', level=-1) -> List[str]:
    ret = list_sub_folders(folder, pattern, level)
    ret = [str(f) for f in ret]
    return ret


def list_files(folder: Union[Path, str], pattern: str = '*', level=0) -> List[Path]:
    """List child files of parent folder

    Args:
        folder (Path | str)
        pattern (str, optional): Defaults to '*'.
        level:
            -1: no limit
            0: current folder

    Returns:
        List[Path]: list of files' path
    """
    if not folder:
        raise ValueError("folder is not empty")
    ret = []
    new_level = (level - 1) if level > 0 else level
    for f in os.scandir(folder):
        if f.is_dir() and (level == -1 or level > 0):
            ret.extend(list_files(f.path, pattern=pattern, level=new_level))
        elif f.is_file() and fnmatch(f.name, pattern):
            ret.append(Path(f.path))

    return ret


def list_files_str(folder: Union[Path, str], pattern: str = '*', level=-1) -> List[str]:
    ret = list_files(folder, pattern, level)
    ret = [str(f) for f in ret]
    return ret


def load_file_to_str(file_path: Union[Path, str], encoding="utf-8", errors="ignore") -> str:
    """_summary_

    Args:
        file_path (Path | str)
        encoding (str, optional): Defaults to "utf-8".
        errors (str, optional): Defaults to "ignore".

    Returns:
        str: data of file
    """
    file_path = __convert_path(file_path, b_check_exists=True)

    with open(file_path, "r", encoding=encoding, errors=errors) as f_source:
        s = f_source.read()
    return s


def load_file_to_list_str(file_path: Union[Path, str], b_remove_blank_str=False, encoding="utf-8", errors="ignore") -> List[str]:
    """Load text unicode file to list(string)

    Args:
        encoding (str): default utf-8 (utf-8-sig: UTF8 with bom)
    Returns:
        List[str]: list of string containt file's content
    """
    file_path = __convert_path(file_path, b_check_exists=True)

    with open(file_path, "r", encoding=encoding, errors=errors) as f_source:
        lines = f_source.readlines()

    lines = [x.replace("\n", "") for x in lines if (
        b_remove_blank_str and not is_blank_str(x)) or not b_remove_blank_str]

    return lines

def load_file_to_list_str_n_head(file_path: Union[Path, str], b_remove_blank_str=False, encoding="utf-8", errors="ignore", row_num=10) -> List[str]:
    """Load text unicode file to list(string)

    Args:
        encoding (str): default utf-8 (utf-8-sig: UTF8 with bom)
    Returns:
        List[str]: list of string containt file's content
    """
    file_path = __convert_path(file_path, b_check_exists=True)

    with open(file_path, "r", encoding=encoding, errors=errors) as f_source:
        lines = [next(f_source) for _ in range(row_num)]

    lines = [x.replace("\n", "") for x in lines if (
        b_remove_blank_str and not is_blank_str(x)) or not b_remove_blank_str]

    return lines

def write_str_to_file(file_path: Union[Path, str], data: str, encoding="utf-8", newline="\n"):
    """Write string data to text unicode file

    Args:
        encoding (str): default utf-8 (utf-8-sig: UTF8 with bom)
        newline (str): None, '', '\\n', '\\r', and '\\r\\n'
    """
    file_path = __convert_path(file_path, b_create_parent=True)
    if is_blank_str(data):
        raise ValueError("data is not empty")

    with open(file_path, "w+", encoding=encoding, newline=newline) as f_dest:
        f_dest.write(data)


def write_list_str_to_file(file_path: Union[Path, str], data: List[str], b_remove_blank_str=False, newline="\n", encoding="utf-8"):
    """Write list of string to unicode file

    Args:
        encoding (str): default utf-8 (utf-8-sig: UTF8 with bom)
        newline (str): None, '', '\\n', '\\r', and '\\r\\n'
    """
    file_path = __convert_path(file_path, b_create_parent=True)
    if not is_list(data):
        raise ValueError("data must be list(str)")

    new_data = []
    for item in data:
        if b_remove_blank_str and is_blank_str(item):
            continue
        if item.endswith("\n"):
            new_data.append(item)
        else:
            new_data.append(item + "\n")

    with open(file_path, "w+", newline=newline, encoding=encoding) as f_dest:
        f_dest.writelines(new_data)


def append_str_to_file(file_path: Union[Path, str], data, encoding="utf-8"):
    """Append string data to end of unicode file

    Args:
        file_path (str): path of source file
        data (str): data
        encoding (str): default utf-8 (utf-8-sig: UTF8 with bom)
    """
    file_path = __convert_path(file_path)
    if is_blank_str(data):
        raise ValueError("data is not empty")

    file_path.parent.mkdir(exist_ok=True)

    with open(file_path, "a", encoding=encoding) as f_dest:
        f_dest.write(data)


def append_list_str_to_file(file_path: Union[Path, str], data: List[str], b_remove_blank_str=False, newline=None, encoding="utf-8"):
    """Append string data to end of unicode file

    Args:
        encoding (str): default utf-8 (utf-8-sig: UTF8 with bom)
        newline (str): None, '', '\\n', '\\r', and '\\r\\n'
    """
    file_path = __convert_path(file_path)
    if not is_list(data):
        raise ValueError("data must be list(str)")

    n = len(data)
    with open(file_path, "a", encoding=encoding, newline=newline) as f_dest:
        for i, item in enumerate(data):
            if b_remove_blank_str and is_blank_str(item):
                continue
            if i < n - 1 and "\n" not in item:
                item += "\n"
            f_dest.write(item)


def create_zip(src: Union[Path, str], dst: Union[Path, str] = ""):
    """Create a zip file

    Args:
        src : source folder
        dst : dest file

    """
    src = __convert_path(src)
    dst = __convert_path(dst, b_create_parent=True) if dst else src

    if dst.suffix != 'zip':
        dst = dst.with_suffix(".zip")

    zf = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
    abs_src = os.path.abspath(src)
    for dirname, _, files in os.walk(src):
        for filename in files:
            absname = os.path.abspath(os.path.join(dirname, filename))
            arcname = absname[len(abs_src) + 1:]
            zf.write(absname, arcname)
    zf.close()


def extract_zip(src: Union[Path, str], dst: Union[Path, str, None] = ""):
    """Create a zip file

    Args:
        src : source folder
        dst : dest file
    """

    if not src:
        raise ValueError("src is not empty")
    src = __convert_path(src, b_check_exists=True)
    if not dst:
        dst = src.parent / src.stem
    dst = __convert_path(dst)
    dst.mkdir(exist_ok=True)

    with zipfile.ZipFile(src, "r") as zip_ref:
        zip_ref.extractall(dst)


def create_folder(dest_folder: Union[Path, str], force_delete=False):
    """Create new folder

    Args:
        dest_folder (str): dest folder
        force_delete (bool, optional): True: delete exists folder
    """
    if not dest_folder:
        raise ValueError("Destination folder is not empty")
    if isinstance(dest_folder, Path):
        dest_folder = str(dest_folder)

    if os.path.isdir(dest_folder) and force_delete:
        shutil.rmtree(dest_folder, True)
    elif os.path.isfile(dest_folder):
        raise ValueError(f"File {dest_folder} existed")

    if not os.path.isdir(dest_folder) and not os.path.islink(dest_folder):
        os.makedirs(dest_folder)


def load_json_file(
    file_path: Union[Path, str], parse_float=None, parse_int=None, parse_constant=None, object_pairs_hook=None, encoding="utf-8"
):
    """Load json data from file

    Returns:
        dict: json data

    """
    file_path = __convert_path(file_path, b_check_exists=True)

    with open(file_path, "r", encoding=encoding) as f_source:
        json_data = json.load(
            f_source,
            parse_float=parse_float,
            parse_int=parse_int,
            parse_constant=parse_constant,
            object_pairs_hook=object_pairs_hook,
            # encoding="utf-8",    python 3.10 not need
        )
    return json_data



class UniversalEncoder(json.JSONEncoder):
    ENCODER_BY_TYPE = {
        datetime.datetime: lambda o: o.isoformat(),
        datetime.date: lambda o: o.isoformat(),
        datetime.time: lambda o: o.isoformat(),
        set: list,
        frozenset: list,
        GeneratorType: list,
        bytes: lambda o: o.decode(),
        BaseModel: lambda o: o.dict(),
    }

    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        for k, v in self.ENCODER_BY_TYPE.items():
            if isinstance(obj, k):
                encoder = v
                return encoder(obj)
        return super().default(obj)


def write_dict_to_json_file(file_path: Union[Path, str], data: Union[dict, list], encoding="utf-8", newline="\n", indent=4):
    """Write dict data to text file with json format

    Args:
        file_path (str): dest file path
        data (dict): dictionary data
        encoding (str):
    """
    file_path = __convert_path(file_path, b_create_parent=True)

    with open(file_path, "w+", encoding=encoding, newline=newline) as f_dest:
        # Save direct to text file
        json.dump(data, f_dest, ensure_ascii=False, indent=indent, cls=UniversalEncoder)


def get_current_dir(path: Union[Path, str]) -> Path:
    """Get current dir of path

    Args:
        path (str): source path

    Returns:
        str
    """
    return __convert_path(path).parent


def process_files_in_folder(*args, folder: Union[Path, str] = "", func=None, pattern: str = '*', level=0):
    """

    Args:
        func : Must be func_name(file_path, *args)
    """
    folder = __convert_path(folder, b_check_exists=True)
    if not func:
        raise ValueError("Invalid parameter 'func'")

    files = list_files(folder, pattern, level)

    for _ in files:
        func(_, *args)


def is_binary_file(file_path: Union[Path, str]):
    """Return true if the given filename is binary.

    Raises an EnvironmentError if the file does not exist or cannot be
    accessed.
    """
    file_path = __convert_path(file_path, b_check_exists=True)

    fin = open(file_path, "rb")
    ret = False
    try:
        CHUNK_SIZE = 1024
        while 1:
            chunk = fin.read(CHUNK_SIZE)
            if 0 in chunk:  # found null byte
                ret = True
                break
            if len(chunk) < CHUNK_SIZE:
                break  # done
    finally:
        fin.close()

    return ret

def copy_folder(src: Union[Path, str], dest: Union[Path, str], b_overwrite: bool = True, ignore_types: List[str] = None, include_types: List[str] = None, ignore_folder: List[str] = None, b_recursive=True):
    """Copy src/* to dest/*

    Args:
        src (_type_): _description_
        dest (_type_): _description_
        b_overwrite (bool, optional): Overwrite?. Defaults to True.
        ignore_types (list, optional): Ignore types. Example: ['chm','html']. Defaults to None.
        include_types (list, optional): Include types. Example: ['chm','html']. Defaults to None.
        ignore_folder (list, optional): Ignore folders. Example: folder1. Defaults to None.
        b_recursive (bool, optional): Copy subfolder's contents.. Defaults to True.

    Raises:
        RuntimeError: _description_
    """
    src = __convert_path(src, True)
    dest = __convert_path(dest)

    if src.is_file() or src.is_symlink():
        return
    dest.mkdir(parents=True, exist_ok=True)
    for f in src.glob('*'):
        if f.is_dir():
            if ignore_folder and f.name in ignore_folder:
                continue
            if b_recursive:
                copy_folder(f, dest / f.name, b_overwrite=b_overwrite, ignore_types=ignore_types, include_types=include_types, ignore_folder=ignore_folder, b_recursive=b_recursive
                            )
            else:
                (dest / f.name).mkdir(parents=True, exist_ok=True)
        else:
            file_type = f.suffix.lstrip('.')
            if ignore_types and file_type in ignore_types:
                continue
            if (include_types and f.suffix.lstrip('.') in include_types) or not include_types:
                shutil.copy(f, dest)