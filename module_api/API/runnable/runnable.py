# Python Libraries
import os
from typing_extensions import Tuple, Type
import pathlib
import argparse
import logging
import sys
import requests

# API Libraries
import module_api.API.lock as lock
import module_api.API.logging as log
from module_api.API.backend.utils.utils import get_jwt, get_backend_endpoint

# Runnable to be ran by the lock
class Runnable:
    lock_type   : Type[lock.CaliciLock] = lock.CaliciLock
    REQUIRED_ATTRIBUTES  = [
        'init', 're_init', 'run', 'stop'
    ]
    """
        The init function initializes all the object required for running the
        runnable. The function determines if a re_init is required or an init is
        required.
    """
    def __init__(self, lock_path : pathlib.Path, logger_name : str = __file__):
        # Append the parent path
        sys.path.append(pathlib.Path(__file__).parent)
        # Check if it is currently debug mode
        DEBUG       = os.environ.get('DEBUG', True)
        # Init checks
        self.__init_checks()
        # Load the lock file
        self.lock                       = self.__load_lockfile(lock_path)
        # Setup logging
        self.logger, self.logger_name   = self.__setup_logging(
            self.lock, logger_name, DEBUG
        )
        self.debug  = DEBUG

    def __load_lockfile(self, path : pathlib.Path) -> lock.CaliciLock:
        Lock    = self.lock_type
        if Lock is None:
            raise ValueError('Runnable lock_type cannot be none')
        elif not issubclass(Lock, lock.CaliciLock):
            raise ValueError(
                'Runnable lock_type have to be a subclass of CaliciLock'
            )
        return Lock(path)

    def __setup_logging(self,
        lock : lock.CaliciLock, logger_name : str = __file__,
        debug : bool = True
    ) -> Tuple[logging.Logger, str]:
        # Modify debug level base on debug variable
        debug_level         = logging.DEBUG
        # Setup logger with some name
        logger              = logging.getLogger(logger_name)
        logger.setLevel(debug_level)
        # Stream Handling
        stream_handler      = logging.StreamHandler()
        stream_handler.setFormatter(log.VerboseColourfulFormatter())
        logger.addHandler(stream_handler)
        # File based logging
        log_path    = lock.header.log_path
        if log_path and not log_path.is_dir():
            file_handler    = log.FileLogger(log_path, debug_level)
            file_handler.setFormatter(log.VerboseBWFormatter())
            logger.addHandler(file_handler)
        else: logger.warning(
            f'File at {str(log_path)} cannot be found or is a folder'
        )
        return (logger, logger_name)
    # Check FUnctions
    def __init_checks(self):
        required    = self.REQUIRED_ATTRIBUTES
        b_req_list  = [hasattr(self, require) for require in required]
        if not all(b_req_list):
            raise NotImplementedError(f"""
                One of the following classes have not been implemented
                {required}
                the following have been implemented
                {b_req_list}
            """)

    # Internal Functions for running
    def _initialize(self):
        lock    = self.lock

        # Now call user implemented functions
        lock_init   = self.lock.status.initialized
        # Reinit the module if it has nver been initialized and only re init if
        # it has been initialized
        if lock_init:
            self.re_init(lock)
        else:
            self.init(lock)
            lock.set(status = {'initialized' : True})

    def _run(self):
        lock    = self.lock
        debug   = self.debug
        self.run(lock, debug)

    def _stop(self):
        lock    = self.lock
        debug   = self.debug
        self.lock.stop()
        self.stop(lock, debug)
    
    def _exception_handler(self, e : Exception):
        self.lock.error()
        self.logger.error("Exception: ", exc_info=True)
        self.exception_handler(e)

    # Initializes the object for the first time (First Run init)
    def init(self,
        lock : lock.CaliciLock, debug : bool = True
    ):
        raise NotImplementedError(
            'init() function have to be implemented'
        )

    # Initializes the object subsequently, opened while running, etc.
    def re_init(self,
        lock : lock.CaliciLock, debug : bool = True
    ):
        raise NotImplementedError(
            're_init() function have to be implemented'
        )

    # Run the runnable
    def run(self,
        lock : lock.CaliciLock, debug : bool = True
    ):
        raise NotImplementedError(
            'run() function have to be implemented'
        )

    # Run after raising an instance of StopRunnable
    def stop(self,
        lock : lock.CaliciLock, debug : bool = True
    ):
        raise NotImplementedError(
            'stop() function have to be implemented'
        )

    # Run when exceptions happen in the runnable
    # Default to just logging the exception
    def exception_handler(self, exc : Exception):
        logging.exception(exc)

    # Does argument parsing
    @staticmethod
    def create(Runnable : Type):
        parser  = argparse.ArgumentParser()
        parser.add_argument(
            '--lock', type = str, help = 'path to the lock file'
        )
        args    = parser.parse_args()
        runnable= Runnable(args.lock)
        return runnable
