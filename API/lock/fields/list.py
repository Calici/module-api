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
        raise AssertionError(f'child has to be of type {Lock.LockField}')
      self._child = child

      if maxLength < 0:
           raise AssertionError(f'Max Length has to be a positive number')
      self._maxLength = maxLength
      self._child_type = copy.deepcopy(child)
      super().__init__(list, default)
      self._buffer = [] 


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
            "type" : "append", "elm" : elm
        })
    def reorder_array_by_index(self, arr : List[int]):
            reordered_arr = []
            for index in arr:
                if 0 <= index < len(self._value):
                    reordered_arr.append(self._value[index])
            return reordered_arr

    def reorder(self, newOrder: List[int]):
        reordered_arr = self.reorder_array_by_index(newOrder)
        self._value = reordered_arr
        self._buffer.append({
            "type": "reorder",
            "newOrder": newOrder
        })

    def modify(self, pos : int, elm : T):
        self._value[pos] = elm
        self._buffer.append({
            "type":"modify", "pos":pos, "elm":elm
        })
    def remove(self, pos : int):
        del self._value[pos]
        self._buffer.append({
            "type":"remove", "pos":pos
        })
    def empty(self):
        self._value = []
        self._buffer.append({
            "type":"empty"
        })
    def flush(self):
        self._buffer = []




K = TypeVar("K")
class TupleField(Lock.LockField[Tuple[K]], Generic[K]):
    """
        TupleField, basically a list field but with non modifiable length
    """
    def __init__(
        self,
        children: Union[List[Lock.LockField[K]], Tuple[Lock.LockField[K]]],
        default: Union[Tuple[K], None] = None,
        length: int = 0
    ):
        try:
            for child in children:
                assert isinstance(child, Lock.LockField)
        except AssertionError:
            raise AssertionError(f'children have to be of type {Lock.LockField}')
        
        self._children = children

        if length < 0:
            raise AssertionError('Length has to be a positive number')
        self._length = length
        self._children = copy.deepcopy(children)
        super().__init__(tuple, default)
        self._value = tuple(None for _ in range(length))
        self._buffer = []

    def validate(self, value: List[K]) -> List[K]:
        validated_value = []
        for i in range(len(value)):
            val = value[i]
            validated_value.append(self._children[i].validate(val))
        return list(validated_value)

    def _assertLength(self, value: List[K]) -> List[K]:
        if len(value) != self._length:
            raise AssertionError('Length of the tuple should be fixed')
        else:
            return value

    def _set_value(self, value: List[K], change: bool = True):
        value = self.validate(value)
        for i in range(len(value)):
            field = copy.deepcopy(self._children[i])
            field._set_value(value[i])
            value[i] = field.serialize() #type:ignore
        self._value = value
        self._changed = change

    def serialize(self) -> JSONSerializable:
        build_list = []
        for val in self._value:
            for i in range(len(val)):   #type:ignore
                self._children[i]._set_value(val[i], False)  #type:ignore
            build_list.append(tuple(child.serialize() for child in self._children))
        return build_list

    def modify(self, pos: int, elm: K):

        if pos < 0 or pos >= len(self._value):
            raise IndexError("Index out of range")


        value_list = list(self._value)
        value_list[pos] = elm
        self._value = tuple(value_list)

        self._buffer.append({
            "type": "modify", "pos": pos, "elm": elm
        })

        

    def flush(self):
        super().flush()
        self._changed = False
