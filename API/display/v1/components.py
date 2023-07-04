# API Imports
import API.lock as lock

# Library Imports
from typing import Any, List, Union, Dict

# A base type for table types
class TableType(lock.LockSection):
    type        = lock.LockField(type = str)
    zoomable    = lock.LockField(type = bool, default = False)
    sortable    = lock.LockField(type = bool, default = False)

# A Base for all tables, override required parts
class BaseTable(lock.LockSection):
    headers = lock.ListField(child = lock.LockField(str))
    rows    = lock.ListField(
        child = lock.ListField(child = lock.LockField(str))
    )
    types   = lock.ListField(child = TableType())

# A Mutable Table
class MutableTable(BaseTable):
    def add_headers(self, header_name : str, column_default : Any):
        # Append to headers and mark changes
        headers     = self.headers
        headers.append(header_name)

        # Add an empty column
        rows        = self.rows
        for row in self.rows:
            row.append(column_default)
        
        self.set(
            headers = headers, rows = rows
        )

    def add_rows(self, row_value : list):
        rows        = self.rows
        rows.append(row_value)
        self.set(
            rows = rows
        )
    # This sets the rows, only use if you are really sure about it
    def set_rows(self, row_value : List[List]):
        self._fields['rows']._value = row_value
        self.mark_changed()
        self._fields['rows'].mark_changed()

# Progress Field
# class ProgressField(lock.LockField):
#     def __init__(self, default : float = None):
#         super().__init__(float, default)
