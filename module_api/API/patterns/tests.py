from unittest import TestCase
from .file_lock import FileLock
from module_api.API.test import DirectoryGenerator, random_string
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor
import random
import sys
import pathlib

def read_or_write(kwargs : dict):
    fpath : pathlib.Path = kwargs['fpath']
    value : str = kwargs['value']
    if random.random() < 0.5:
        with FileLock(fpath).lock() as f:
            written_length = f.write(value)
            assert written_length == len(value)
    else:
        with FileLock(fpath).lock_shared() as f:
            out = f.read().strip()
            try:
                assert value == out
            except AssertionError:
                print(f"{len(value)} != {len(out)}", file = sys.stderr)
                raise


class FileLockTest(TestCase):
    def test_lock_multiprocessing(self):
        with DirectoryGenerator() as d:
            fpath = d / 'lol.txt'
            to_write = random_string(5_000_000)
            with open(fpath, 'w') as f:
                f.write(to_write)
            with Pool() as p:
                p.map(
                    read_or_write, 
                    [{ 'fpath' : fpath, 'value' : to_write}] * 1000
                )
    def test_lock_multithreading(self):
        with DirectoryGenerator() as d:
            fpath = d / 'lol.txt'
            to_write = random_string(5_000_000)
            with open(fpath, 'w') as f:
                f.write(to_write)
            with ThreadPoolExecutor() as p:
                p.map(
                    read_or_write,
                    [{ 'fpath' : fpath, 'value' : to_write}] * 100
                )