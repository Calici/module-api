import module_api.API.lock as lock
from .common import \
    Messages, \
    v0_ProgressField, \
    ControlConfig, \
    v0_MutableTable, \
    DisplayStatus

class ComponentWithTable(lock.LockSection):
    version = lock.LockField(type = str, default = '0.0')
    progress = v0_ProgressField()
    messages = Messages()
    controls = ControlConfig()
    start_time = lock.DateTimeField()
    table = v0_MutableTable()
    status =lock.LockField[DisplayStatus](str, default = 'INIT')

    def __init__(self, buffer_length : int = 10, **kwargs):
        self.messages._max_length = buffer_length
        super().__init__(**kwargs)