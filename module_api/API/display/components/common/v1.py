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

class ControlConfig(lock.LockSection):
    show_run = lock.LockField(type = bool, default = True)
    show_stop = lock.LockField(type = bool, default = True)

class Message(lock.LockSection):
    title = lock.LockField(type = str, default = 'A Message Title')
    content = lock.LockField(type = str, default = '')

def SmartBoxes(
    default : List[Dict[str, Any]] = [], optimize_merge : bool = False
) -> lock.ListField[Dict[str, Any], SmartBox]:
    return lock.ListField(
        lock.SpreadKwargs(SmartBox), default, optimize_merge = optimize_merge
    )

def Messages(
    default : List[Dict[str, Any]] = [], optimize_merge : bool = False
) -> lock.ListField[Dict[str, Any], Message]:
    return lock.ListField(
        lock.SpreadKwargs(Message), default, optimize_merge = optimize_merge
    )