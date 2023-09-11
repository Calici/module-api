from __future__ import annotations
# API Imports
import module_api.API.lock as lock

# Library Imports
from typing import \
    List, \
    Union, \
    Callable, \
    Any, \
    Dict, \
    List, \
    Any, \
    TypedDict

from .common import \
    v1_ProgressField, \
    v1_ControlConfig, \
    v1_SmartBoxes, \
    v1_TimeField, \
    v1_Messages
    

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

class RowListField(lock.ListField[
    List[Dict[str, Any]], 
    lock.TupleField[Dict[str, Any], CellT]
]):
    def __init__(self, 
        row_types : List[Callable[[Any], CellT]], *args, **kwargs
    ):
        super().__init__(
            lock.TypeField(lock.TupleField, row_types),
            *args, 
            optimize_merge = False,
            **kwargs
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

    class HeaderT(TypedDict):
        displayName : str
        type : Union[
            TableType_ZoomableSortableI, 
            TableTypeImg, 
            TableTypeButtonAPII, 
            TableTypeButtonRedirectI
        ]
    @staticmethod
    def create_header(
        config : List[HeaderT]
    ) -> lock.TupleField[Dict[str, Any], Header]:
        return lock.TupleField([
            lambda v : Header(entry['type'], **v)
            for entry in config
        ], [{
            'displayName' : entry['displayName']
        } for entry in config
        ], optimize_merge = False)

class MutableTable(lock.LockSection):
    headers : lock.TupleField[Dict[str, Any], Header]
    rows : RowListField
    def __init__(self, 
        headers : lock.TupleField[Dict[str, Any], Header], 
        rows : RowListField     
    ):
        self.headers = headers
        self.rows = rows
        super().__init__()

    def sort_rows(self, 
        column_id : int, 
        reverse : bool = False, 
        compare_function : Callable[[Any], Any] = 
            lambda x : x 
    ):
        indexes = list(range(len(self.rows)))
        indexes.sort(
            key = lambda id : compare_function(
                self.rows.get()[id].get()[column_id].get()
            ), 
            reverse = reverse
        )
        self.rows.reorder(indexes)

class ComponentWithTable(lock.LockSection):
    version = lock.LockField(type = str, default = '1.0')
    progress = v1_ProgressField()
    messages = v1_Messages()
    status = lock.LockField(str, default = '')
    controls = v1_ControlConfig()
    time = v1_TimeField()
    smartboxes = v1_SmartBoxes()
    table : MutableTable
    def __init__(self, 
        table : MutableTable, buffer_length : int = 10, **kwargs
    ):
        self.table = table
        self.messages._max_length = buffer_length
        super().__init__(**kwargs)