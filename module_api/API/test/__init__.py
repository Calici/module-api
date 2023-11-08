import string
import random
from pathlib import Path
from typing_extensions import \
  Union
import shutil

def random_string(length : int) -> str:
    return ''.join(
       [random.choice(string.ascii_lowercase) for i in range(length)]
    )

class DirectoryGenerator:
    __slots__ = [ 'fd_path' ]
    def __init__(self, parent_path : Union[Path, None] = None):
        if parent_path is not None:
            self.fd_path = parent_path / 'tmp' / random_string(10)
        else:
            self.fd_path = Path('/tmp', random_string(10))
        self.fd_path.mkdir(parents = True, exist_ok = True)
    
    def __enter__(self) -> Path:
        return self.fd_path

    def __exit__(self, *args):
        shutil.rmtree(self.fd_path)

    def __del__(self):
        if self.fd_path.exists():
            shutil.rmtree(self.fd_path)

def generate_test_fd(
    parent_path : Union[Path, None] = None
) -> DirectoryGenerator:
    """
        Creates a directory that automatically cleans up on exit. 
        Usage :
            with generate_test_fd() as fd:
                fd : pathlib.Path
    """
    return DirectoryGenerator(parent_path)


__all__ = [
    'generate_test_fd',
    'random_string'
]