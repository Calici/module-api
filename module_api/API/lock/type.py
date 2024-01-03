from typing_extensions import \
    TypeVar, \
    Callable, \
    Dict, \
    Any, \
    Type
from .field import \
    LockBase
from .section import \
    LockSection


V = TypeVar('V', bound = LockBase)
T = TypeVar('T')
K = TypeVar('K')

def TypeField(Field : Callable[[K, T], V], type : K) -> Callable[[T], V]:
    def x(v : T):
        return Field(type, v)
    return x

S = TypeVar('S', bound = LockSection)
def SpreadKwargs(Field : Type[S]) -> Callable[[Dict[str, Any]], S]:
    def x(v : Dict[str, Any]):
        return Field(**v)
    return x