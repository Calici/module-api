from unittest import TestCase
from .file_lock import FileLock
from module_api.API.test import DirectoryGenerator, random_string
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor
import random
import time

def read_or_write(kwargs : dict):
    flock = kwargs['flock'] if 'flock' in kwargs else FileLock(kwargs['fpath'])
    value : str = kwargs['value']
    if random.random() < 0.5:
        with flock.lock() as f:
            time.sleep(random.random() * 0.1)
            written_length = f.write(value)
            assert written_length == len(value)
    else:
        with flock.lock_shared() as f:
            time.sleep(random.random() * 0.1)
            out = f.read().strip()
            try:
                assert value == out
            except AssertionError:
                raise

class FileLockTest(TestCase):
    def test_fuzz_lock_multiprocessing(self):
        with DirectoryGenerator() as d:
            fpath = d / 'lol.txt'
            to_write = random_string(5_000_000)
            with open(fpath, 'w') as f:
                f.write(to_write)
            with Pool() as p:
                p.map(
                    read_or_write, 
                    [{ 'fpath' : fpath, 'value' : to_write}] * 10
                )
    def test_fuzz_lock_multithreading(self):
        with DirectoryGenerator() as d:
            fpath = d / 'lol.txt'
            to_write = random_string(5_000_000)
            with open(fpath, 'w') as f:
                f.write(to_write)
            with ThreadPoolExecutor() as p:
                p.map(
                    read_or_write,
                    [{ 'flock' : FileLock(fpath), 'value' : to_write}] * 2
                )