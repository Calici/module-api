# API Imports
import API.lock as lock
from module_api.API.lock.type import TypeField

# Library Imports
from typing import \
    List, \
    Union, \
    Callable, \
    Any, \
    Dict, \
    List
import datetime

class QueryI(lock.LockSection):
    method = lock.LockField(type = str, default = 'GET')
    requestType = lock.LockField(type = str, default = 'blob')
    endpoint = lock.LockField(type = str, default = "")
    params = lock.LockField(type = dict, default = {})

class TableType_ZoomableSortableI(lock.LockSection):
    type = lock.LockField(type = str, default = "")
    zoomable = lock.LockField(type = bool, default = False)
    sortable = lock.LockField(type = bool, default = False)

class TableTypeImg(lock.LockSection):
    type = lock.LockField(type = str, default = 'img')
    height = lock.LockField(type = int, default = -1)
    width = lock.LockField(type = int, default = -1)

class TableTypeButtonAPII(lock.LockSection):
     type = lock.LockField(type = str, default = 'button')
     action = lock.LockField(type = str, default = 'dl_api')
     src = lock.LockField(type = str, default = "")

class TableTypeButtonRedirectI(lock.LockSection):
     type = lock.LockField(type = str, default = 'button')
     action = lock.LockField(type = str, default = 'redirect')
     config = QueryI()

class TableCellButtonI(lock.LockSection):
    buttonText = lock.LockField(type = str, default = "")
    hiddenText= lock.LockField(type = str, default = "")

class TableCell_ZoomableI(lock.LockSection):
    shortText = lock.LockField(type = str, default = "")
    zoomedText= lock.LockField(type = str, default = "")
class TableCell_ImgI(lock.LockSection):
    src = lock.LockField(type = str, default = "")
    textString = lock.LockField(type = str, default = "")

CellT = Union[
    lock.LockField[str], 
    lock.LockField[int], 
    TableCellButtonI, 
    TableCell_ZoomableI, 
    TableCell_ImgI
]

class RowList(lock.ListField):
    def __init__(self, 
        row_types : List[Callable[[Any], CellT]], *args, **kwargs
    ):
        super().__init__(
            child_constructor = TypeField(lock.TupleField, row_types), 
            *args, **kwargs
        )
class Header(lock.LockSection):
    displayName = lock.LockField(type = str, default = "")
    type : Union[
        TableType_ZoomableSortableI, 
        TableTypeImg, 
        TableTypeButtonAPII, 
        TableTypeButtonRedirectI
    ]
    def __init__(self, 
        header_type :  Union[
            TableType_ZoomableSortableI, 
            TableTypeImg, 
            TableTypeButtonAPII, 
            TableTypeButtonRedirectI
        ], **kwargs
    ):
        self.type = header_type
        super().__init__(**kwargs)

class MutableTable(lock.LockSection):
    # headers = lock.ListField(child = Header())
    def __init__(self, 
        header_list: lock.ListField[Dict[str, Any], Header], 
        row_list: lock.ListField[List[CellT], RowList]
    ):
        self.headers = header_list
        self.rows = row_list
        super().__init__()
        
    def append_rows(self, row : List[Any]):
        self.rows.append(self.rows._child.validate(row))

    def modify_rows(self, pos : int, row : List[Any]):
        self.rows.modify(pos, self.rows._child.validate(row))

    def sort_Row(self, 
        column_index: int, 
        reverse: bool = False, 
        compare_function: Callable = lambda x: x
    ) -> None:
        rows = self.rows.get()
        indexes = list(range(len(rows)))
        indexes.sort(
            key = lambda id : compare_function(
                rows[id].get()[column_index].serialize()
            ), 
            reverse = reverse
        )
        self.rows.reorder(indexes)

class ProgressField(lock.LockSection):
    value = lock.LockField(type=float, default=0.0)
    bouncy = lock.LockField(type=bool, default=False)
class SmartBox(lock.LockSection):
    type=lock.LockField(type=int, default=0)
    title=lock.LockField(type=str, default="")
    content=lock.LockField(type=str, default="")

class TimeField(lock.LockSection):
    startTime=lock.DateTimeField(default = datetime.datetime.now())
    timeDelta=lock.LockField(type=int, default=1)
    
class ControlConfig(lock.LockSection):
    show_run    = lock.LockField(type = bool, default = True)
    show_stop   = lock.LockField(type = bool, default = True)
