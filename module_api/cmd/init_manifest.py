from .base import ActionHandler
import pathlib
import shutil

MANIFEST_TEMPLATE = pathlib.Path(__file__).parent / 'manifest_template.json'
MANIFEST_VALIDATE = pathlib.Path(__file__).parent / 'manifest-validate.json'

class InitManifestHandler(ActionHandler):
    def action(self):
        shutil.copyfile(MANIFEST_TEMPLATE, self.manifest.path)
        shutil.copyfile(
            MANIFEST_VALIDATE, 
            self.manifest.path.parent / 'manifest-validate.json'
        )
        