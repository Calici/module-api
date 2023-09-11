from .common import \
    v1_ProgressField, \
    v1_ControlConfig, \
    v1_TimeField, \
    v1_Messages
import module_api.API.lock as lock

class ComponentWithoutTable(lock.LockSection):
    version = lock.LockField(type = str, default = '1.0')
    progress = v1_ProgressField()
    messages = v1_Messages()
    status = lock.LockField(str, default = '')
    controls = v1_ControlConfig()
    time = v1_TimeField()