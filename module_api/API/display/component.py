# API Imports
import API.lock as lock
import datetime

from .component_fields import \
    MutableTable, \
    ProgressField

class Message(lock.LockSection):
    title = lock.LockField(type = str, default = 'A Message Title')
    content = lock.LockField(type = str, default = 'A Message Content')

class ControlConfig(lock.LockSection):
    show_run = lock.LockField(type = bool, default = True)
    show_stop = lock.LockField(type = bool, default = True)

class BaseComponent(lock.LockSection):
    progress = ProgressField(default = 0.0)