from .base import ActionHandler, TEMPLATE_DIR
import shutil
import pathlib

DOCKER_TEMPLATE = TEMPLATE_DIR / 'dockerfile.tmp'

class InitDockerHandler(ActionHandler):
    def __init__(self, manifest: pathlib.Path, workdir: pathlib.Path):
        super().__init__(manifest, workdir)
        self.docker_path = self.root_dir.parent / 'dockerfile'
        
    def action(self):
        shutil.copyfile(DOCKER_TEMPLATE, self.docker_path)