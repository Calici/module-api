from .base import ActionHandler, ModuleLock
import pathlib
import subprocess
import pathlib

class RunDocker(ActionHandler):
    def __init__(self, manifest: pathlib.Path, workdir: pathlib.Path):
        super().__init__(manifest, workdir)
        self.module_lock = ModuleLock(self.lock_path)
        self.container_name = self.module_lock.docker.container_name.get()

    def action(self):
        run_arguments = self.module_lock.docker.run_argument.get()
        run_command = self.module_lock.docker.run_command.get()
        volumes = [
            entry
            for volume_mapping in self.module_lock.docker.volumes.serialize()
            for entry in ["-v", volume_mapping]
        ]
        subprocess.run([
            "docker", "run", 
            run_arguments, *volumes, self.container_name, run_command
        ])