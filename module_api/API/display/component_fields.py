# API Imports
import module_api.API.lock as lock

# A base type for table types
class TableType(lock.LockSection):
    type        = lock.LockField(type = str, default = "")
    zoomable    = lock.LockField(type = bool, default = False)
    sortable    = lock.LockField(type = bool, default = False)

# A Base for all tables, override required parts
class BaseTable(lock.LockSection):
    headers = lock.ListField(lock.TypeField(lock.LockField, str))
    rows    = lock.ListField(
        lock.TypeField(
            lock.ListField, lock.TypeField(lock.LockField, str) #type: ignore
        ) 
    )
    types   = lock.ListField(lambda e : TableType(**e))

# A Mutable Table
class MutableTable(BaseTable):
   pass
# Progress Field
class ProgressField(lock.LockField):
    def __init__(self, default : float = 0.0):
        super().__init__(float, default)