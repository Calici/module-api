from .base import ActionHandler, ModuleLock
import pathlib
import subprocess

class BuildDocker(ActionHandler):
    def __init__(self, manifest: pathlib.Path, workdir: pathlib.Path):
        super().__init__(manifest, workdir)
        self.module_lock = ModuleLock(self.root_dir / 'module.lock')
        self.internal_name = self.module_lock.module.internal_name.get()
    def action(self):
        subprocess.run([
            "docker", "build", "-t", self.internal_name, "."
        ])