import module_api.API.lock as lock
from .common import \
    v0_Messages, \
    v0_ProgressField, \
    v0_ControlConfig, \
    v0_MutableTable, \
    v0_DisplayStatus

class ComponentWithTable(lock.LockSection):
    version = lock.LockField(type = str, default = '0.0')
    progress = v0_ProgressField()
    messages = v0_Messages()
    controls = v0_ControlConfig()
    start_time = lock.DateTimeField()
    table = v0_MutableTable()
    status =lock.LockField[v0_DisplayStatus](str, default = 'INIT')

    def __init__(self, buffer_length : int = 10, **kwargs):
        self.messages._max_length = buffer_length
        super().__init__(**kwargs)