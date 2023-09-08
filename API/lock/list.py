from typing import \
    List, \
    Generic, \
    TypeVar, \
    Any, \
    Callable, \
    Union

from API.lock.field import JSONSerializable
from .field import LockField
from .section import LockBase
from .types import FieldBuffer, ArrayOpT
import logging

T = TypeVar("T")
V = TypeVar("V", bound = LockBase)
class ListField(LockField[List[V]], Generic[T, V]):
    """
      A ListField, models an array, ensures that all entries of the field have 
      the same type
    """
    def __init__(self, 
        child_constructor : Callable[[T], V], 
        default : List[T] = [], 
        max_length : int = 0, 
        force : bool = False
    ):
        self._child = child_constructor
        self._max_length = self.validate_max_length(max_length)
        self._buffer = FieldBuffer()
        LockField.__init__(self, list, default, force)

    def validate_max_length(self, max_length : int) -> int:
        if max_length < 0:
            raise AssertionError('Max length has to be a positive number')
        return max_length
    
    def make_child(self, value : T) -> V:
        return self._child(value)
    
    def _trimList(self, value : List[T]) -> List[T]:
        if len(value) > self._max_length:
            value = value[len(value) - self._max_length :]
        return value
    
    def validate_one_element(self, value : T) -> V:
        return self.make_child(value)

    def validate(self, value : List[Any]) -> List[V]:
        value = [ self.make_child(entry) for entry in value ]
        if self._max_length > 0:
            value = self._trimList(value)
        return value
    
    def set_value(self, value : Union[List[T], ArrayOpT], change : bool = True):
        if isinstance(value, list):
            self.value = self.validate(value)
        elif isinstance(value, dict):
            self.apply_operation(value)
        self.set_change(change)

    def apply_operation(self, value : ArrayOpT):
        if value['type'] == 'append':
            self.append(value['elm'])
        elif value['type'] == 'reorder':
            self.reorder(value['newOrder'])
        elif value['type'] == 'modify':
            self.modify(value['pos'], value['elm'])
        elif value['type'] == 'empty':
            self.empty()
        elif value['type'] == 'remove':
            self.remove(value['pos'])
        else:
            logging.warning("Invalid Dict {0}".format(str(value)))
    
    def serialize(self) -> List[JSONSerializable]:
        return [
            entry.serialize() for entry in self.value
        ]

    # List Operations
    def append(self, elm : T):
        self.value.append(self.make_child(elm))
        self._buffer.add({
            "type" : "append", 'elm' : elm
        })

    def reorder(self, newOrder : List[int]):
        self.value = [ self.value[i] for i in newOrder ]
        self._buffer.add({
            "type" : "reorder", 'newOrder' : newOrder
        })

    def modify(self, pos : int, elm : T):
        self.value[pos].set(elm)
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

    def __len__(self):
        return len(self.value)