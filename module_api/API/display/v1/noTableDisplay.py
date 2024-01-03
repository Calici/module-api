import module_api.API.lock as lock
from .components import \
    ProgressField, \
    TimeField

class BaseComponent(lock.LockSection):
    version = lock.LockField(type = str, default = '1.0')
    progress = ProgressField()
    messages = lock.ListField(
        child = lock.LockField(str, default = ""), default = []
    )
    status = lock.LockField(
        type = str, default = ''
    )
    # controls    = ControlConfig()
    time = TimeField()
    
    def __init__(self, buffer_length : int = 10, **kwargs):
        self.messages._max_length   = buffer_length
        super().__init__()
        self.set(**kwargs)

