import module_api.API.lock as Lock
import pathlib

class ModuleSection(Lock.LockSection):
    name = Lock.LockField(str, default = '')
    internal_name = Lock.LockField(str, default = '')
    version = Lock.LockField(str, default = '0.0.0')

class DockerSection(Lock.LockSection):
    volumes = Lock.ListField(
        Lock.TypeField(Lock.LockField, str), default = ["./src:/app"]
    )
    container_name = Lock.LockField(str, default = '')
    run_argument = Lock.LockField(str, default = '--rm')
    run_command = Lock.LockField(str, default = 'bash')

class BackendSection(Lock.LockSection):
    endpoint = Lock.LockField(str, default = '')
    backend_fd = Lock.LockField(pathlib.Path, default = pathlib.Path())

class ModuleLock(Lock.LockIO):
    module = ModuleSection()
    docker = DockerSection()
