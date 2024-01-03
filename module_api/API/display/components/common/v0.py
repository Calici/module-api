import module_api.API.lock as lock
from .same import ZoomableField

class TableType(lock.LockSection):
    type = lock.LockField(type = str, default = "")
    zoomable = ZoomableField()
    sortable = lock.LockField(type = bool, default = False)
  
class MutableTable(lock.LockSection):
    headers = lock.ListField(lock.TypeField(lock.LockField, str))
    rows = lock.ListField(
      lock.TypeField(lock.ListField, lock.TypeField(lock.LockField, str)) #type: ignore
    )
    types = lock.ListField(lock.SpreadKwargs(TableType))

class ControlConfig(lock.LockSection):
    show_run = lock.LockField(type = bool, default = True)
    show_stop = lock.LockField(type = bool, default = True)

def ProgressField(default : float = 0.0):
    return lock.LockField(float, default)