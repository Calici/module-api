from typing_extensions import Callable, Any
from watchdog.events import FileSystemEventHandler
from module_api.API.display import Display
import pathlib

class DisplayHandler(FileSystemEventHandler):
    """
        DisplayHandler
        A Handler for the module_api display API to send data based on the 
        changes in the Display.
    """
    __slots__ = (
        'display_dir', 'main_file_path', 'changes_file_path', 'update_hook'
    )
    def __init__(self, 
        display_dir : pathlib.Path, 
        update_hook : Callable[[dict], Any]
    ):
        self.display_dir = display_dir
        self.main_file_path = Display.full_file_path(display_dir)
        self.changes_file_path = Display.changes_file_path(display_dir)
        self.update_hook = update_hook

    def read_file(self):
        pass