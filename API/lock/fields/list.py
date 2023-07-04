import API.lock as Lock
from API.lock.field import JSONSerializable
from typing import Any, List, Type, Union, Generic, TypeVar, Dict, Tuple
import copy


T = TypeVar("T")
class ListField(Lock.LockField[List[T]], Generic[T]):
    """
      A ListField, models an array, ensures that all entries of the field have 
      the same type
    """
    def __init__(self, 
        child : Lock.LockField[T],
        default : Union[List[T], None] = None,
        maxLength : int = 0,
        force : bool = False
    ):
      try:
           assert isinstance(child, Lock.LockField)
      except AssertionError:
        raise AssertionError(f'children have to be of type {Lock.LockField}')
      self._child = child

      if maxLength < 0:
           raise AssertionError(f'Max Length have to a positive number')
      self._maxLength = maxLength
      self._child_type = copy.deepcopy(child)
      super().__init__(List[T], default)



    def validate(self, value : List[T]) -> List[T]:
        for i in range(len(value)):
            val = value[i]
            value[i] = self._child.validate(val)
        if self._maxLength > 0:
            value = self._trimList(value)
        return value

    def _trimList(self, value : List[T]) -> List[T]:
        if len(value) > self._maxLength:
            value = value[len(value) - self._maxLength :]
        return value
    
    def _set_value(self, value : List[T], change : bool = True):
        value = self.validate(value)
        for i in range(len(value)):
            Field = copy.deepcopy(self._child_type)
            Field._set_value(value[i])
            value[i] = Field.serialize() #type: ignore
        self._value = value
        self._changed = change
       
    def serialize(self) -> JSONSerializable:
        build_list = []
        for val in self._value:
            self._child._set_value(val, False)
            build_list.append(self._child.serialize())
        return build_list




    # List Operations
    def append(self, elm : T):
        self._value.append(elm)
        self._buffer.append({
            "type" : "append", elm : elm
        })

    def reorder(self, newOrder : List[int]):

        def reorder_array_by_index(arr, index_arr):
            reordered_arr = []
            for index in index_arr:
                if 0 <= index < len(arr):
                    reordered_arr.append(arr[index])
            return reordered_arr

        reorder_array_by_index(self._value, newOrder)

        self._buffer.append({
            "type":"reorder", List[int]:newOrder
        })
    def modify(self, pos : int, elm : T):
        self._value[pos] = elm
        self._buffer.append({
            "type":"modify", pos:pos, elm:elm
        })
    def remove(self, pos : int):
        self._value.remove(self._value[pos])
        self._buffer.append({
            "type":"remove", pos:pos
        })
    def empty(self):
        self._value = []
        self._buffer.append({
            "type":"remove"
        })
    def flush(self):
        self._buffer = []




K = TypeVar("K")
class TupleField(Lock.LockField[Tuple[K]], Generic[K]):
    """
        TupleField, basically a list field but with non modifiable length
    """
    def __init__(self, 
        children : Union[List[Lock.LockField[K]], Tuple[Lock.LockField[K]]],
        default : Union[Tuple[K], None] = None, 
        length : int = 0
    ):

     try:
         assert isinstance(children, Lock.LockField)
     except AssertionError:
            raise AssertionError(f'child have to be of type {Lock.LockField}')
     self._children  = children
         
     if length < 0:
        raise AssertionError(f'Max Length have to be a positive number')
     self._length = length
     self._children = copy.deepcopy(children)
     super().__init__(Tuple[K], default)



    def validate(self, value : List[K]) -> List[K]:
        for i in range(len(value)):
            val = value[i]
            value[i] = self._children.validate(val)
        return value
    
    def _assertLength(self,value : List[K]) -> List[K]:
        raise NotImplementedError
    

    def _set_value(self, value : List[K], change : bool = True):
        value = self.validate(value)
        for i in range(len(value)):
            Field = copy.deepcopy(self._children) # type: ignore
            Field._set_value(value[i])
            value[i] = Field.serialize()  # type: ignore
        self._value     = value
        self._changed   = change
    
    def serialize(self) -> JSONSerializable:
        build_list = []
        for val in self._value:
            self._children._set_value(val, False)
            build_list.append(self._children.serialize())
        return build_list
    
    # List Operations
    def modify(self, pos : int, elm : K):
        self._value[pos] = elm
        self._buffer.append({
            "type":"modify", pos:pos, elm:elm
        })
    
    def flush(self):
        self._buffer = []
