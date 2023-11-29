from __future__ import annotations
import pathlib
import json
from abc import ABC, abstractmethod
from typing_extensions import \
    TypedDict, \
    Any, \
    Dict, \
    Union, \
    List, \
    Type

TEMPLATE_DIR = pathlib.Path(__file__).parent / 'templates'

ManifestT = TypedDict("ManifestT", {
    "params" : Dict[str, Any],
    "results" : Dict[str, Any],
    "in_nodes" : Dict[str, Any], 
    'params_render' : Dict[str, Any],
    'results_render' : Dict[str, Any],
    'out_nodes' : Dict[str, Any],
    'download_struct' : Dict[str, Any],
    'run_count' : Dict[str, Any],
    'token_prices' : Dict[str, Any],
    'version' : str,
    '$schema' : str
})

class Manifest:
    __slots__ = ('path', )
    def __init__(self, manifest : pathlib.Path):
        self.path = manifest
    
    def get_json(self) -> ManifestT:
        with open(self.path, 'r') as f:
            return json.load(f)
    
    def write_json(self, content : ManifestT):
        with open(self.path, 'w') as f:
            json.dump(content, f)
    
    def validate_exist(self):
        if not self.path.exists():
            raise RuntimeError(f"Manifest does not exist at {self.path}")

class ActionHandler(ABC):
    __slots__ = ('manifest', 'workdir', 'root_dir')
    def __init__(self, manifest : pathlib.Path, workdir : pathlib.Path):
        self.manifest = Manifest(manifest)
        self.workdir = workdir
        self.root_dir = manifest.parent

    @abstractmethod
    def action(self):
        ...

HandlerMapT = Dict[str, Union[Type[ActionHandler], List[str]]]
def make_action(action1 : Union[str, None], action2 : Union[str, None]):
    if action2 is not None and action2 is not None:
        return '{0}.{1}'.format(action1, action2)
    elif action1 is not None:
        return action1
    else:
        raise RuntimeError("At least action1 have to be given")

def exec_handlers(
    handler_map : HandlerMapT,
    action : str, manifest : pathlib.Path, workdir : pathlib.Path
):
    Handler = handler_map[action]
    if isinstance(Handler, list):
        for handler in Handler:
            exec_handlers(handler_map, handler, manifest, workdir)
    else:
        Handler(manifest, workdir).action()