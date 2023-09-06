# API Imports
import API.lock as lock

# Library Imports
from typing import Any, List, Union, Dict, Callable

# A base type for table types
class QueryI(lock.LockSection):
    method = lock.LockField(type = str, default='GET')
    requestType = lock.LockField(type = str, default='blob')
    endpoint = lock.LockField(type = str)
    params = lock.LockField(type = any)

class TableType_ZoomableSortableI(lock.LockSection):
    type        = lock.LockField(type = str)
    zoomable    = lock.LockField(type = bool, default = False)
    sortable    = lock.LockField(type = bool, default = False)
class TableTypeImg(lock.LockSection):
    type = lock.LockField(type = str, default = 'img')
    height = lock.LockField(type = int)
    width = lock.LockField(type = int)
class TableTypeButtonAPII(lock.LockSection):
     type = lock.LockField(type = str, default = 'button')
     action = lock.LockField(type = str, default = 'dl_api')
     src = lock.LockField(type = str)
class TableTypeButtonRedirectI(lock.LockSection):
     type = lock.LockField(type = str, default = 'button')
     action = lock.LockField(type = str, default = 'redirect')
     config= QueryI()
     
    

class TableCellButtonI(lock.LockSection):
    buttonText = lock.LockField(type=str)
    hiddenText= lock.LockField(type=str)
class TableCell_ZoomableI(lock):
    shortText = lock.LockField(type=str)
    zoomedText= lock.LockField(type=str)
class TableCell_ImgI(lock.LockSection):
    src = lock.LockField(type=str)
    textString = lock.LockField(type=str)


# A Base for all tables, override required parts
# class BaseTable(lock.LockSection):
#     headers = lock.ListField(child = lock.LockField(str))
#     rows    = lock.ListField(
#         child = lock.ListField(child = lock.LockField(any))
#     )
#     types   = lock.ListField(child = TableType_ZoomableSortableI())

# A Mutable Table
class Header(lock.LockSection):
    def __init__(self, 
        display_name: str, 
        type_instance:  Union[
            TableType_ZoomableSortableI, 
            TableTypeImg, 
            TableTypeButtonAPII, 
            TableTypeButtonRedirectI
        ]
    ):
        self.displayName= display_name
        self.type = type_instance
        super().__init__()

class Row(lock.LockSection):
    def __init__(self, 
        row: Union[
            str, 
            int, 
            TableCellButtonI, 
            TableCell_ZoomableI, 
            TableCell_ImgI
        ]
    ):
        self.row = row
        super().__init__()

class MutableTable(lock.LockSection):
    # headers = lock.ListField(child = Header())
    def __init__(self, header_list: List[Header], row_list: List[Row]):
        self.headers = header_list
        self.rows = row_list
        super().__init__()
        
    def add_rows(self, row_value : Row):
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

    def sort_Row(self, column_index: int, 
                 reverse: bool = False, 
                compare_function: Callable = lambda x: x) -> None:
        self.rows.sort(key=lambda 
                       row: compare_function(row.row[column_index]), 
                       reverse=reverse)

