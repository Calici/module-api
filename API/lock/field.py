# Library Imports
from __future__ import annotations
from datetime import datetime
from typing import \
    Any, \
    List, \
    Type, \
    Union, \
    Generic, \
    TypeVar, \
    Dict
from pypharmaco.structure.field import \
    Field, \
    BaseField
from abc import abstractmethod

JSONSerializable    = Union[
    None, int, str, bool, float, datetime,
    List['JSONSerializable'], Dict[str, 'JSONSerializable']
]

"""
    LockBase -> implements the changes API
"""
T = TypeVar("T")
class LockBase(BaseField[T], Generic[T]):
    def __init__(self):
        self._changed = False
    def is_changed(self) -> bool:
        return self._changed
    def flush(self):
        self._changed = False
    def mark_changed(self):
        self._changed = True
    def set_change(self, change : bool):
        self._changed = change
    @abstractmethod
    def serialize(self) -> JSONSerializable:
        ...
    @abstractmethod
    def serialize_changes(self) -> JSONSerializable:
        ...
    @abstractmethod
    def set_value(self, value : T, changed : bool = True):
        ...
    @abstractmethod
    def get(self) -> T:
        ...
    @abstractmethod
    def set(self, value : Any):
        ...
    @abstractmethod
    def validate(self, value: T | str) -> T:
        ...

"""
    LockField -> LockFile Fields, a base class for most lock files
    The methods common to all LockSection, and LockField :

    flush() -> mark the field as not changed
    mark_changed() -> mark the field as changed
    serialize() -> serialize the lock field to a dict that is dumpable
    serialize_changes() -> serializer only the CHANGED data
    changed() -> return the status of the field
    get_value() -> get the value
    set(value or kwargs) -> set value
"""
class LockField(Generic[T],  Field[T], LockBase[T]):
    RETURN_RAW_FIELDS = (
        int, str, bool, float, list, dict, datetime
    )
    def __init__(self, 
        type : Union[Type[T], None], default : T, force : bool = True
    ):
        Field.__init__(self, type, default, allow_none = not force)
        LockBase.__init__(self)
        
    def serialize(self) -> JSONSerializable:
        if isinstance(self.value, LockField.RETURN_RAW_FIELDS):
            return self.value
        else:
            return str(self.value)
            
    def serialize_changes(self) -> JSONSerializable:
        """
            Serialize the field only if the field already changed
        """
        if self.is_changed():
            return self.serialize()
        else:
            return None
        
    def set_value(self, value: T, changed: bool = True):
        Field.set(self, value)
        self.set_change(changed)
    
    def set(self, value : Any):
        self.set_value(value)