import module_api.API.lock as lock
from typing import \
  List, \
  Dict, \
  Any

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

class Message(lock.LockSection):
    title = lock.LockField(type = str, default = 'A Message Title')
    content = lock.LockField(type = str, default = '')

def Messages(
    default : List[Dict[str, Any]] = [], optimize_merge : bool = False
) -> lock.ListField[Dict[str, Any], Message]:
    return lock.ListField(
        lock.SpreadKwargs(Message), default, optimize_merge = optimize_merge
    )

class ControlConfig(lock.LockSection):
    show_run = lock.LockField(type = bool, default = True)
    show_stop = lock.LockField(type = bool, default = True)