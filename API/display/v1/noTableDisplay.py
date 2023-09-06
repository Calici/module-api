import API.lock as lock
import datetime

# Local Imports



class ProgressField(lock.LockSection):
    value = lock.LockField(type=float, default=0.0)
    bouncy = lock.LockField(type=bool, default=False)
class TimeField(lock.LockSection):
    startTime=lock.DateTimeField(default=datetime.datetime.now())
    timeDelta=lock.LockField(type=int, default=1)
class ControlConfig(lock.LockSection):
    show_run    = lock.LockField(type = bool, default = True)
    show_stop   = lock.LockField(type = bool, default = True)

class BaseComponent(lock.LockSection):
    version = lock.LockField(type = str, default = '1.0')
    progress    = ProgressField()
    messages    = lock.ListField(
        child = lock.LockField(str)
    )
    status      = lock.LockField(
        type = str, default = ''
    )
    # controls    = ControlConfig()
    time= TimeField()
    
    def __init__(self, buffer_length : int = 10, **kwargs):
        self.messages._max_length   = buffer_length
        super().__init__()
        self.set(**kwargs)

