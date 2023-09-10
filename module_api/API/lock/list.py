from typing import \
    List, \
    Generic, \
    TypeVar, \
    Any, \
    Callable, \
    Union

from module_api.API.lock.field import JSONSerializable
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
        force : bool = False, 
        optimize_merge : bool = False
    ):
        self._child = child_constructor
        self._max_length = self.validate_max_length(max_length)
        self._buffer = FieldBuffer()
        self._optimize = optimize_merge
        LockField.__init__(self, list, default, force)
        self._buffer.clear()

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
            self.empty()
            for entry in value: self.append(entry)
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
    #TODO: Correctly implement _optimize mode
    def serialize_changes(self) -> JSONSerializable:
        if self._optimize:
            return self._buffer.data #type: ignore
        else:
            return super().serialize_changes()

    # List Operations
    def append(self, elm : T):
        if self._max_length != 0 and len(self) == self._max_length:
            self.remove(0)
        self.value.append(self.make_child(elm))
        self._buffer.add({
            "type" : "append", 'elm' : elm
        })
        self.mark_changed()

    def reorder(self, newOrder : List[int]):
        self.value = [ self.value[i] for i in newOrder ]
        self._buffer.add({
            "type" : "reorder", 'newOrder' : newOrder
        })
        self.mark_changed()

    def modify(self, pos : int, elm : T):
        self.value[pos].set_value(elm)
        self._buffer.add({
            "type" : "modify", 'pos' : pos, 'elm' : elm
        })
        self.mark_changed()

    def remove(self, pos : int):
        del self.value[pos]
        self._buffer.add({"type" : "remove", 'pos' : pos})
        self.mark_changed()

    def empty(self):
        self.value = []
        self._buffer.add({"type" : "empty"})
        self.mark_changed()

    def flush(self):
        self._buffer.clear()
        super().flush()

    def clear_buffer(self):
        self._buffer.clear()

    def __len__(self):
        return len(self.value)