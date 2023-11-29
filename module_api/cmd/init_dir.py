from .base import ActionHandler, TEMPLATE_DIR, ModuleLock
import pathlib
from slugify import slugify
import shutil
import subprocess

GITIGNORE_TEMPLATE = TEMPLATE_DIR / '.gitignore.tmp'
DOCKERIGNORE_TEMPLATE = TEMPLATE_DIR / '.dockerignore.tmp'

class InitDir(ActionHandler):
    def __init__(self, manifest : pathlib.Path, workdir : pathlib.Path):
        super().__init__(manifest, workdir)
        self.module_lock = ModuleLock(self.root_dir / 'module.lock')
        self.gitignore_path = self.root_dir / '.gitignore'
        self.dockerignore_path = self.root_dir / '.dockerignore'
    
    def get_template(self, name : str, internal_name : str):
        return {
            'module' : { 'name' : name, 'internal_name' : internal_name }
        }

    def action(self):
        module_name = input('Enter module name : ')
        internal_module_name = slugify(module_name)
        
        self.module_lock.set(
            **self.get_template(module_name, internal_module_name)
        )
        subprocess.run(["git", "init"])
        shutil.copyfile(GITIGNORE_TEMPLATE, self.gitignore_path)
        shutil.copyfile(DOCKERIGNORE_TEMPLATE, self.dockerignore_path)
        