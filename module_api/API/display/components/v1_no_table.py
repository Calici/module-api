from .common import \
    v1_ProgressField, \
    v1_TimeField, \
    Messages, \
    DisplayStatus, \
    ControlConfig

import module_api.API.lock as lock

class ComponentWithoutTable(lock.LockSection):
    version = lock.LockField(type = str, default = '1.0')
    progress = v1_ProgressField()
    messages = Messages()
    status = lock.LockField[DisplayStatus](str, default = 'INIT')
    controls = ControlConfig()
    time = v1_TimeField()