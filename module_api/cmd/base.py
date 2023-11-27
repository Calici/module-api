import pathlib
import json
from abc import ABC, abstractmethod
from typing_extensions import \
    TypedDict, \
    Any, \
    Dict

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
    __slots__ = ('manifest', 'workdir')
    def __init__(self, manifest : pathlib.Path, workdir : pathlib.Path):
        self.manifest = Manifest(manifest)
        self.workdir = workdir

    @abstractmethod
    def action(self):
        ...