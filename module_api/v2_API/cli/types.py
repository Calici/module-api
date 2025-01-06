from typing import Annotated, List
import pydantic

def validate_version(v : str):
    major, minor, patch = v.split('.')
    major = int(major)
    minor = int(minor)
    patch = int(patch)

class ModuleVersion(pydantic.BaseModel):
    version : Annotated[int, pydantic.AfterValidator(validate_version)]
    commit_id : str

class Module(pydantic.BaseModel):
    name : str
    internal_name : str
    description : str
    icon : str
    dark_icon : str
    versions: List[ModuleVersion]

# Default Module Directory Structure
"""
root
- src/
    - run.py
    - lock.py
- assets/
    - icon.svg
    - dark_icon.svg
- module.yaml.lock
"""

class ModuleLock(pydantic.BaseModel):
    module : Module
    