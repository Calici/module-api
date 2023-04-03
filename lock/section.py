# Library Imports
from typing import Dict, Any
import copy

# Local Imports
from .field import LockField

"""
    LockSection -> can be used to create sections in lockfiles
    Most recursive logic is implemented here so that lock file updates 
    are efficient
"""
class LockSection(LockField):
    def __init__(self, **kwargs):
        self._fields    = self._get_fields()
        self._set_value(kwargs, False)
        self._changed   = False
    # Internally Useful Functions
    ## Field Building
    def _get_fields(self):
        fields : Dict[str, LockField]   = {}
        field_dict = {i : getattr(self, i) for i in dir(self)}
        for k, v in field_dict.items():
            if isinstance(v, LockField): fields[k] = copy.deepcopy(v)
        return fields
    # Field values
    ## Validation
    def validate(self, value : Any):
        return value
    ## Value setting internal
    def _set_value(self, kwargs : dict, change : bool = True):
        self.validate(kwargs)
        for k, v in kwargs.items():
            try:
                field   = self._fields[k]
                try:
                    val_func= getattr(self, f'validate_{k}')
                    v   = val_func(v)
                except AttributeError: pass
                field._set_value(v, change)
                self._changed = change
            except KeyError: continue
    ## Real value setting
    def set(self, **kwargs):
        self._set_value(kwargs)
    ## Getting values
    def get(self) -> dict:
        build_dict  = {}
        for k, v in self._fields.items():
            build_dict[k]   = v.get()
        return build_dict
    ## To get only one key
    def __getitem__(self, key : str) -> LockField:
        return self._fields[key]

    def __setitem__(self, key : str, val : Any):
        self._fields[key]
        self.set(**{key : val})
    ## To get with attribute instead of the key
    def __getattribute__(self, __name: str) -> LockField:
        original    = super().__getattribute__(__name)
        if isinstance(original, LockSection) and __name in self._fields:
            return self._fields[__name]
        elif isinstance(original, LockField) and __name in self._fields:
            return self._fields[__name].get()
        return original

    ## So that things work correctly
    def __getattr__(self, __name : str):
        return super().__getattribute__(__name)

    ## __eq__ comparator
    def __eq__(self, other):
        if isinstance(other, LockSection):
            for k, v in self._fields.items():
                try:
                    if not(other._fields[k] == v): return False
                except KeyError: return False
            return True
        elif isinstance(other, dict):
            for k, v in self._fields.items():
                try:
                    if not(v == other[k]): return False
                except KeyError: return False
            return True
        return False
    ## Serializing
    def serialize(self) -> dict:
        build_dict  = {}
        for k, v in self._fields.items():
            build_dict[k]   = v.serialize()
        return build_dict
    ## Only changes
    def serialize_changes(self) -> dict:
        build_dict  = {}
        for k, v in self._fields.items():
            if v.changed(): build_dict[k] = v.serialize_changes()
        return build_dict
    # Changes marking
    def flush(self):
        for v in self._fields.values(): v.flush()
        self._changed   = False