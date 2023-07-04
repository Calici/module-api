import API.lock as lock
import datetime

# Local Imports
from .components import MutableTable, ProgressObjectField


class ProgressField(lock.LockSection):
    value = lock.LockField(type=float, default=0.0)
    bouncy = lock.LockField(type=bool, default=False)
class SmartBox(lock.LockSection):
    type=lock.LockField(type=int, default=0)
    title=lock.LockField(type=str, default="")
    content=lock.LockField(type=str, default="")

class TimeField(lock.LockSection):
    startTime=lock.DateTimeField(default=datetime.datetime.now())
    timeDelta=lock.LockField(type=int, default=1)
class ControlConfig(lock.LockSection):
    show_run    = lock.LockField(type = bool, default = True)
    show_stop   = lock.LockField(type = bool, default = True)

class BaseComponent(lock.LockSection):
    version = lock.LockField(type = str, default = '1.0')
    table= MutableTable()
    progress    = ProgressField()
    messages    = lock.ListField(
        child = lock.LockField(str)
    )
    status      = lock.LockField(
        type = str, default = ''
    )
    # controls    = ControlConfig()
    time= TimeField()
    smartBoxes=lock.ListField(child=SmartBox())
    
    def __init__(self, buffer_length : int = 10, **kwargs):
        self.messages._max_length   = buffer_length
        super().__init__()
        self.set(**kwargs)

class ComponentWithTable(BaseComponent):
    table       = MutableTable()

class SimpleComponent(BaseComponent):
    pass