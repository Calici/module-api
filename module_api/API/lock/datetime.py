from .field import LockField
from typing import Union
import datetime

class DateTimeField(LockField[datetime.datetime]):
    def __init__(self, default : datetime.datetime = datetime.datetime.now()):
        super().__init__(datetime.datetime, default)
    
    def serialize(self) -> str:
        return self.value.isoformat()
    
    def validate(self, value : Union[str, datetime.datetime]):
        try:
            if isinstance(value, str):
                return datetime.datetime.fromisoformat(value)
            elif isinstance(value, datetime.datetime):
                return value
        except:
            raise TypeError("Datetime Conversion Failed {0}".format(value))
        raise TypeError("Type Conversion Error {0}".format(type(value)))
