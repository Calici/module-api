# Local Imports
from __future__ import annotations
from pypharmaco.structure import Section
from .field import LockBase
from typing_extensions import \
    Dict, \
    Any

"""
    LockSection -> can be used to create sections in lockfiles
    Most recursive logic is implemented here so that lock file updates 
    are efficient
"""
class LockSection(Section[LockBase], LockBase[Dict[str, Any]]):
    def __init__(self, **kwargs):
        LockBase.__init__(self)
        self._fields = self._build_fields()
        self.set_value(kwargs, False)
    
    def validate(self, value : Dict[str, Any]):
        return value

    def set(self, **kwargs):
        self.set_value(kwargs)

    def set_value(self, value: Dict[str, Any], changed: bool = True):
        for field_name, field_value in value.items():
            try:
                self.get_field(field_name).set_value(field_value, changed)
            except KeyError:
                pass
        self.set_change(changed)

    def get(self):
        return self.serialize()
    
    def serialize(self) -> dict:
        return {
            field_name : field.serialize()
            for field_name, field in self.items()
        }
    
    def serialize_changes(self) -> dict:
        return {
            field_name : field.serialize_changes()
            for field_name, field in self.items() if field.is_changed()
        }
    
    def flush(self):
        LockBase.flush(self)
        for field in self.values():
            field.flush()