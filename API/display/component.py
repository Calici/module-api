# Library Import

# API Imports
import API.lock as lock
import datetime

# Local Imports
from .component_fields import MutableTable, ProgressField

class Message(lock.LockSection):
    title       = lock.LockField(type = str, default = 'A Message Title')
    content     = lock.LockField(type = str, default = '')

class ControlConfig(lock.LockSection):
    show_run    = lock.LockField(type = bool, default = True)
    show_stop   = lock.LockField(type = bool, default = True)

class BaseComponent(lock.LockSection):
    progress    = ProgressField(default = 0.0)
    messages    = lock.ListField(
        child = lock.LockField(str)
    )
    status      = lock.LockField(
        type = str, default = ''
    )
    controls    = ControlConfig()
    start_time  = lock.DateTimeField(
        default = datetime.datetime.now()
    )
    
    def __init__(self, buffer_length : int = 10, **kwargs):
        self.messages._max_length   = buffer_length
        super().__init__()
        self.set(**kwargs)

class ComponentWithTable(BaseComponent):
    table       = MutableTable()

class SimpleComponent(BaseComponent):
    pass