import pathlib
from typing import List, Union

def create_directories(
    workdir : pathlib.Path, 
    dir_list : List[Union[str, pathlib.Path]], 
    permission : int = 0o775
):
    for dir in dir_list:
        path    = workdir / dir
        path.mkdir(permission, True, True)