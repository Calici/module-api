import API.lock as Lock
from API.lock.field import JSONSerializable
from typing import Any, List, Type, Union, Generic, TypeVar, Dict, Tuple

T = TypeVar("T")
class ListField(Lock.LockField[List[T]], Generic[T]):
    """
      A ListField, models an array, ensures that all entries of the field have 
      the same type
    """
    def __init__(self, 
        child : Lock.LockField[T],
        default : Union[List[T], None] = None,
        maxLength : int = 0,
        force : bool = False
    ):
      """
        child : the child to use for verification
        default : The default value to use for initialization
        max_length : maximum length of the list, cuts the list if it is too long
        force : if dynamic type checking should be enforced
      """
      raise NotImplementedError

    def validate(self, value : List[T]) -> List[T]:
        raise NotImplementedError

    def _trimList(self, value : List[T]) -> List[T]:
        raise NotImplementedError
  
    def _set_value(self, value : List[T], change : bool = True):
        raise NotImplementedError
       
    def serialize(self) -> JSONSerializable:
        raise NotImplementedError

    # List Operations
    def append(self, elm : T):
        raise NotImplementedError
    def reorder(self, newOrder : List[int]):
        raise NotImplementedError
    def modify(self, pos : int, elm : T):
        raise NotImplementedError
    def remove(self, pos : int):
        raise NotImplementedError
    def empty(self):
        raise NotImplementedError
    def flush(self):
        raise NotImplementedError

K = TypeVar("K")
class TupleField(Lock.LockField[Tuple[K]], Generic[K]):
    """
        TupleField, basically a list field but with non modifiable length
    """
    def __init__(self, 
        children : Union[List[Lock.LockField[K]], Tuple[Lock.LockField[K]]],
        default : Union[Tuple[K], None] = None, 
        length : int = 0
    ):
        """
            children : a list or tuple of some length that decodes the entries
            default : The default value to give
            length : the Length of the tuple
        """
        raise NotImplementedError

    def validate(self, value : List[K]) -> List[K]:
        raise NotImplementedError
    def _assertLength(value : List[K]) -> List[K]:
        raise NotImplementedError
    def _set_value(self, value : List[K], change : bool = True):
        raise NotImplementedError
    
    def serialize(self) -> JSONSerializable:
        raise NotImplementedError
        # List Operations
    def append(self, elm : K):
        raise NotImplementedError
    def reorder(self, newOrder : List[int]):
        raise NotImplementedError
    def modify(self, pos : int, elm : K):
        raise NotImplementedError
    def remove(self, pos : int):
        raise NotImplementedError
    def empty(self):
        raise NotImplementedError
    def flush(self):
        raise NotImplementedError