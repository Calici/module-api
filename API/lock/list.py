from typing import \
    List, \
    Generic, \
    TypeVar, \
    Any
from .field import LockField, JSONSerializable
from .section import LockBase
from .types import FieldBuffer
import copy

T = TypeVar("T")
class ListField(LockField[List[T]], Generic[T]):
    """
      A ListField, models an array, ensures that all entries of the field have 
      the same type
    """
    def __init__(self, 
        child : LockBase[T],
        default : List[T] = [],
        max_length : int = 0,
        force : bool = False
    ):
      self._child = self.validate_child(copy.deepcopy(child))
      self._max_length = self.validate_max_length(max_length)
      self._buffer = FieldBuffer()
      super().__init__(list, default, force)

    def validate_child(self, child : Any) -> LockBase[T]:
        try:
            assert isinstance(child, LockBase)
        except AssertionError:
            raise AssertionError('Child has be of type {0}'.format(LockBase))
        return child
    
    def validate_max_length(self, max_length : int) -> int:
        if max_length < 0:
            raise AssertionError('Max length has to be a positive number')
        return max_length

    def validate(self, value : List[T]) -> List[T]:
        value = [
            self._child.validate(entry) for entry in value
        ]
        if self._max_length > 0:
            value = self._trimList(value)
        return value

    def _trimList(self, value : List[T]) -> List[T]:
        if len(value) > self._max_length:
            value = value[len(value) - self._max_length :]
        return value
    
    def set_value(self, value : List[T], change : bool = True):
        self.value = self.validate(value)
        self._changed = change
       
    def serialize(self) -> JSONSerializable:
        build_list = []
        for val in self.value:
            self._child.set_value(val, False)
            build_list.append(self._child.serialize())
        return build_list

    # List Operations
    def append(self, elm : T):
        self.value.append(elm)
        self._buffer.add({
            "type" : "append", 'elm' : elm
        })

    def reorder(self, newOrder : List[int]):
        self.value = [ self.value[i] for i in newOrder ]
        self._buffer.add({
            "type" : "reorder", 'newOrder' : newOrder
        })

    def modify(self, pos : int, elm : T):
        self.value[pos] = elm
        self._buffer.add({
            "type" : "modify", 'pos' : pos, 'elm' : elm
        })
    def remove(self, pos : int):
        del self.value[pos]
        self._buffer.add({"type" : "remove", 'pos' : pos})

    def empty(self):
        self.set([])
        self._buffer.add({"type" : "empty"})

    def clear_buffer(self):
        self._buffer.clear()

