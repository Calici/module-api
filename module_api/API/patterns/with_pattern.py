from typing_extensions import \
    TypeVar, \
    Generic, \
    Callable, \
    Any

T = TypeVar('T')
class WithPattern(Generic[T]):
    def __init__(self, 
        creator : Callable[[], T], 
        cleanup : Callable[[T], Any]
    ):
        self.creator = creator
        self.cleanup = cleanup
        self.is_run = False
        self.is_cleaned = True
    
    def __enter__(self) -> T:
        self._temp = self.creator()
        self.is_run = True
        self.is_cleaned = False
        return self._temp

    def __exit__(self, *args):
        if not self.is_cleaned:
            self.cleanup(self._temp)
            self.is_cleaned = True

    def __del__(self):
        if not self.is_cleaned:
            self.cleanup(self._temp)
            self.is_cleaned = True