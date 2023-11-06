from .field import \
    JSONSerializable, \
    LockBase, \
    LockField
from typing_extensions import \
    List, \
    Generic, \
    TypeVar, \
    Any
from .types import FieldBuffer
import copy

K = TypeVar("K")
class TupleField(LockField[List[K]], Generic[K]):
    """
        TupleField, basically a list field but with non modifiable length
    """
    def __init__(self, 
        children : List[Any],
        default : List[K] = [], 
        length : int = 0,
        force : bool = True
    ):
     self._length = length
     self._children = self.validate_children([
         copy.deepcopy(child) for child in children
     ])
     self._buffer = FieldBuffer()
     super().__init__(list, default, force)
    
    def validate_children(self, children : Any) -> List[LockBase[K]]:
        try:
            assert all(isinstance(child, LockBase) for child in children)
        except AssertionError:
            raise AssertionError('Child has be of type {0}'.format(LockBase))
        return children

    def validate(self, value : List[K]) -> List[K]:
        return [
            child.validate(entry) for entry, child in zip(value, self._children)
        ]
    
    def _assertLength(self, value : List[K]) -> List[K]:
        if len(value) != self._length:
            raise AssertionError(f'Length of array should be fixed')
        else:
            return value

    def set_value(self, value : List[K], change : bool = True):
        self.value = self.validate(value)
        self._changed = change
    
    def serialize(self) -> JSONSerializable:
        build_list = []
        for entry, child in zip(self.value, self._children):
            child.set_value(entry, False)
            build_list.append(child.serialize())
        return build_list
    
    def modify(self, pos : int, elm : Any):
        self.value[pos] = elm
        self._buffer.add({
            "type" : "modify", 'pos' : pos, 'elm' : elm
        })
    def clear_buffer(self):
        self._buffer.clear()