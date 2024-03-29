from module_api.API.lock.field import JSONSerializable
from .field import \
    JSONSerializable, \
    LockBase, \
    LockField
from typing_extensions import \
    List, \
    Generic, \
    TypeVar, \
    Any, \
    Callable, \
    Union
from .types import FieldBuffer, ArrayOpT
import logging

T = TypeVar('T')
V = TypeVar('V', bound = LockBase)
class TupleField(LockField[List[V]], Generic[T, V]):
    """
        TupleField, implemented as an immutable list. The init class should
        initialize the field. 
    """
    def __init__(self, 
        children : List[Callable[[T], V]], 
        default : List[T] = [], 
        force : bool = True, 
        optimize_merge : bool = False
    ):
        self._length = len(children)
        self._buffer = FieldBuffer()
        self._children = children
        self._optimize = optimize_merge
        LockField.__init__(self, list, default, force)
        self._buffer.clear()
        
    def make_child(self, idx : int, value : T) -> V:
        return self._children[idx](value)
    
    def validate(self, value : List[Any]) -> List[V]:
        if len(value) != self._length:
            raise ValueError(
                "Length Mismatch, expected {0} but got {1}".format(
                    self._length, len(value)
                )
            )
        value = [
            self.make_child(i, value[i]) for i in range(len(value))
        ]
        return value
    
    def set_value(self, value : Union[List[T], ArrayOpT], change : bool = True):
        if isinstance(value, list):
            self.value = self.validate(value)
        elif isinstance(value, dict):
            self.value = self.apply_operation(value)
        self.set_change(change)
    
    def apply_operation(self, value : ArrayOpT):
        if value['type'] == 'modify':
            self.modify(value['pos'], value['elm'])
        else: 
            logging.warning('Invalid Dict {0}'.format(str(value)))
    
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

    def modify(self, pos : int, elm : T):
        self.value[pos].set_value(elm)
        self._buffer.add({
            'type' : 'modify', 'pos' : pos, 'elm' : elm
        })
    
    def clear_buffer(self):
        self._buffer.clear()

    def __len__(self):
        return len(self.value)