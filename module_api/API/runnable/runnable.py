from __future__ import annotations
import os
import abc
from typing_extensions import \
    Tuple, \
    Type, \
    Generic, \
    TypeVar
import pathlib
import argparse
import logging
import sys
import module_api.API.lock as Lock
import module_api.API.logging as log

T = TypeVar('T', bound = Lock.CaliciLock)
class Runnable(Generic[T], abc.ABC):
    lock_type : Type[T]
    def __init__(self, lock_path : pathlib.Path, logger_name : str = __file__):
        sys.path.append(str(pathlib.Path(__file__)))
        self.lock = self.__load_lockfile(lock_path)
        self.logger, self.logger_name = self.__setup_logging(logger_name)

    def is_debug(self) -> bool:
        try:
            return self.debug
        except AttributeError:
            self.debug = os.environ.get('DEBUG', 'true') == 'true'
            return self.debug

    # Private Functions
    def initialize(self):
        if self.lock.status.initialized.get():
            self.init()
            self.lock.set(status= {"initialized" : True})
        else:
            self.re_init()

    def __load_lockfile(self, path : pathlib.Path) -> T:
        if self.lock_type is None:
            raise ValueError('lock_type: cannot be none')
        elif not issubclass(self.lock_type, Lock.CaliciLock):
            raise ValueError("lock_type: have to be a subclass of CaliciLock")
        return self.lock_type(path)
    def __setup_logging(
        self, logger_name : str = __file__
    ) -> Tuple[logging.Logger, str]:
        debug_level = logging.DEBUG if self.is_debug() else logging.WARN
        logger = logging.getLogger(logger_name)
        logger.setLevel(debug_level)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(log.VerboseColourfulFormatter())
        logger.addHandler(stream_handler)
        log_path = self.lock.header.log_path.get()
        if not log_path.is_dir():
            file_handler = log.FileLogger(log_path, debug_level)
            file_handler.setFormatter(log.VerboseBWFormatter())
            logger.addHandler(file_handler)
        else:
            logger.warning(
                f"File at {str(log_path)} cannot be found or is a folder"
            )
        return logger, logger_name

    @abc.abstractmethod
    def init(self):
        ...
    @abc.abstractmethod
    def re_init(self):
        ...
    @abc.abstractmethod
    def run(self):
        ...
    @abc.abstractmethod
    def stop(self):
        ...
    def exception_handler(self, e : Exception):
        self.logger.exception(e)

V = TypeVar('V', bound = Runnable)
def create(Runnable : Type[V]) -> V:
    parser = argparse.ArgumentParser()
    parser.add_argument('--lock', type = str, help = 'path to the lock file')
    args = parser.parse_args()
    runnable = Runnable(args.lock)
    return runnable

def default_run(runnable : Runnable):
    try:
        runnable.initialize()
        runnable.run()
    except Exception as e:
        runnable.exception_handler(e)