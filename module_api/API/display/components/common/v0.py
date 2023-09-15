import module_api.API.lock as lock
from typing import \
  List, \
  Union, \
  Literal

DisplayStatus = Union[
    Literal['INIT'], Literal['COMPLETE'], Literal['STOP'], Literal['RUNNING']
]

class TableType(lock.LockSection):
    type = lock.LockField(type = str, default = "")
    zoomable = lock.LockField(type = bool, default = False)
    sortable = lock.LockField(type = bool, default = False)
  
class MutableTable(lock.LockSection):
    headers = lock.ListField(lock.TypeField(lock.LockField, str))
    rows = lock.ListField(
      lock.TypeField(lock.ListField, lock.TypeField(lock.LockField, str)) #type: ignore
    )
    types = lock.ListField(lock.SpreadKwargs(TableType))

def ProgressField(default : float = 0.0):
  return lock.LockField(float, default)

def Messages(
    default : List[str] = [], optimize_merge : bool = False
):
    return lock.ListField(
        lock.TypeField(lock.LockField, str), default, 
        optimize_merge = optimize_merge
    )

class ControlConfig(lock.LockSection):
    show_run = lock.LockField(type = bool, default = True)
    show_stop = lock.LockField(type = bool, default = True)