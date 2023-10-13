import module_api.API.lock as lock
import datetime
from typing import \
    List, \
    Dict, \
    Any

class ProgressField(lock.LockSection):
    value = lock.LockField(type = float, default = 0.0)
    bouncy = lock.LockField(type = bool, default = False)

class SmartBox(lock.LockSection):
    type = lock.LockField(type = int, default = 0)
    title = lock.LockField(type = str, default = "")
    content = lock.LockField(type = str, default = "")

class TimeField(lock.LockSection):
    startTime = lock.DateTimeField(default = datetime.datetime.now())
    timeDelta = lock.LockField(type = int, default = 1)

def SmartBoxes(
    default : List[Dict[str, Any]] = [], optimize_merge : bool = False
) -> lock.ListField[Dict[str, Any], SmartBox]:
    return lock.ListField(
        lock.SpreadKwargs(SmartBox), default, optimize_merge = optimize_merge
    )
