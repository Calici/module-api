# Library Imports
from __future__ import annotations
from datetime import datetime
from typing import Any, List, Type, Union, Generic, TypeVar, Dict
import copy

JSONSerializable    = Union[
    None, int, str, bool, float, datetime,
    List['JSONSerializable'], Dict[str, 'JSONSerializable']
]

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
T = TypeVar("T")
class LockFieldBase(Generic[T]):
    def __init__(self, type : Type[T]):
        self._type : Type[T]    = type
        self._changed : bool    = False
    
    # Public Functions  
    def changed(self) -> bool: 
        """
            Returns a telling if the field have changed before.
        """
        return self._changed
    def flush(self): 
        """
            Sets the field to unchanged WITHOUT changing its content. 
        """
        self._changed = False
    def mark_changed(self):
        """
            Mark the field to changed WITHOUT changing its content.
        """
        self._changed = True
    def serialize(self) -> JSONSerializable:
        """
            Serialize the field regardless of the changes tag
        """
        raise NotImplementedError
    
    def serialize_changes(self) -> JSONSerializable:
        """
            Serialize the field only if the field already changed
        """
        if self._changed: return self.serialize()
        else: return None
    
V = TypeVar("V")
class LockField(LockFieldBase[V]):
    def __init__(self, type : Type[V], default : Union[V, Any] = None):
        """
            Creates a LockField with type type and default value default. 
            Calls the empty constructor if default is not given.
        """
        super().__init__(type)
        self._set_init_value(default)
    
    # Public API
    def set(self, value : Any):
        """
            Sets the value of the LockField. This sets the LockField to changed
        """
        self._set_value(value)
    def get(self) -> V:
        """
            Gets the value of the LockField. This sets the LockField to a value.
        """
        return self._value
    def validate(self, value : Any) -> V:
        """
            Validates the field, performs conversion, anything imaginable.
        """
        # Default Implementation
        try:
            if isinstance(value, self._type):
                return value
            value   = self._type(value)
            return value
        except ValueError:
            raise TypeError(f'{value} cannot be converted to {self._type}')
    def serialize(self) -> JSONSerializable:
        if isinstance(
            self._value, (int, str, bool, float, datetime, list, dict)
        ):
            return self._value
        else:
            return str(self._value)

    # Private API
    def _set_init_value(self, default : Any):
        if default is not None: 
            self._set_value(default, False)
        else:
            self._value = self._type()

    def _set_value(self, value : Any, change : bool = True):
        validated_value     = self.validate(value)
        self._value         = validated_value
        self._changed       = change
    
    ## == overload, important for comparison !
    def __eq__(self, other):
        if isinstance(other, LockField):
            return self._value == other._value
        elif isinstance(other, self._type):
            return self._value == other
        else: return False

class ListField(LockField[list]):
    def __init__(self, 
        child : LockField, default : Any = None, max_length : int = 0, 
        force : bool = False
    ):
        # Make sure that there is no error
        try:
            assert isinstance(child, LockField)
        except AssertionError:
            raise AssertionError(f'child have to be of type {LockField}')
        self._child     = child
        # Validate MaxLength
        if max_length < 0:
            raise AssertionError(f'Max Length have to be a positive number')
        self._max_length= max_length
        self._child_type= copy.deepcopy(child)
        super().__init__(list, default)
    
    def validate(self, value : List[Any]) -> list:
        for i in range(len(value)):
            val         = value[i]
            value[i]    = self._child.validate(val)
        if self._max_length > 0:
            value       = self._trim_list(value)
        return value
    
    def _set_value(self, value : Any, change : bool = True):
        value   = self.validate(value)
        for i in range(len(value)):
            Field       = copy.deepcopy(self._child_type)
            Field._set_value(value[i])
            value[i]    = Field.serialize()
        self._value     = value
        self._changed   = change
    
    # Private Function Specific to ListField
    def _trim_list(self, value : list) -> list:
        if len(value) > self._max_length:
            value   = value[len(value) - self._max_length : ]
        return value

    def serialize(self) -> JSONSerializable:
        # Serialize Children if required
        build_list  = []
        for val in self._value:
            self._child._set_value(val, False)
            build_list.append(self._child.serialize())
        return build_list

class DateTimeField(LockField):
    def __init__(self, default : datetime = datetime.now()):
        super().__init__(datetime, default)
    def serialize(self) -> str:
        value   : datetime  = self._value
        return value.isoformat()
    def validate(self, value : str):
        try:
            if(isinstance(value, str)):
                return datetime.fromisoformat(value)
            elif isinstance(value, datetime):
                return value
        except:
            raise TypeError(f"Datetime conversion failed {value}")
        raise TypeError(f"Type conversion error {type(value)}")