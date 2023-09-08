import API.lock as lock

# Local Imports
from .components import \
    MutableTable, \
    ProgressField, \
    TimeField, \
    SmartBox

class DisplayWithTableComponent(lock.LockSection):
    version = lock.LockField(type = str, default = '1.0')
    progress    = ProgressField()
    messages    = lock.ListField(
        child = lock.LockField(str, default = ""), default = []
    )
    status      = lock.LockField(
        type = str, default = ''
    )
    # controls    = ControlConfig()
    time = TimeField()
    smartBoxes = lock.ListField()
    
    table : MutableTable
    def __init__(self,
        table : MutableTable,
        buffer_length : int = 10, 
        **kwargs
    ):
        self.table = table
        self.messages._max_length   = buffer_length
        super().__init__()
        self.set(**kwargs)



