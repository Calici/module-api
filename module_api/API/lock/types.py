from typing_extensions import \
    Literal, \
    Tuple, \
    List, \
    Union, \
    Any, \
    overload, \
    TypedDict

class AppendT(TypedDict):
    type : Literal['append']
    elm : Any

class ReorderT(TypedDict):
    type : Literal['reorder']
    newOrder : List[int]

class ModifyT(TypedDict):
    type : Literal['modify']
    pos : int
    elm : Any

class RemoveT(TypedDict):
    type : Literal['remove']
    pos : int

class EmptyT(TypedDict):
    type : Literal['empty']

ArrayOpT = Union[
    AppendT, 
    ReorderT, 
    ModifyT, 
    RemoveT, 
    EmptyT
]

class FieldBuffer:
    def __init__(self, initial_data : List[ArrayOpT] = []):
        self.data = list(initial_data)
    def add(self, op : ArrayOpT):
        self.data.append(op)

    @overload
    def __getitem__(self, entry : Tuple[int, Literal["append"]]) -> AppendT:
        ...
    @overload
    def __getitem__(self, entry : Tuple[int, Literal["reorder"]]) -> ReorderT:
        ...
    @overload
    def __getitem__(self, entry : Tuple[int, Literal["modify"]]) -> ModifyT:
        ...
    @overload
    def __getitem__(self, entry : Tuple[int, Literal["remove"]]) -> RemoveT:
        ...
    @overload
    def __getitem__(self, entry : Tuple[int, Literal["empty"]]) -> EmptyT:
        ...
    def __getitem__(self, entry : Tuple[int, str])-> ArrayOpT:
        idx, type = entry
        if type is None:
            return self.data[idx]
        elif type is not None and self.data[idx]["type"] == type:
            return self.data[idx]
        else:
            raise TypeError("Different Type of return value expected")
    def __setitem__(self, idx : int, elm : ArrayOpT):
        self.data[idx] = elm
    def __len__(self) -> int:
        return len(self.data)
    def clear(self):
        self.data = []