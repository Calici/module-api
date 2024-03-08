from module_api.cmd.base import \
    ModuleLock, \
    ActionHandler, \
    Container
from .build_docker import BuildDocker
from .validate import ContainerValidate
import subprocess
import sys


class ContainerDeploy(ActionHandler):
    def __init__(self, lock: ModuleLock, use_confirm: bool = True):
        super().__init__(lock)
        self.container = Container(lock)
        self.use_confirm = use_confirm

    def validate(self):
        validator = ContainerValidate(self.lock)
        validator.action()

    def run_build(self):
        builder = BuildDocker(self.lock)
        builder.action()

    def action(self):
        print("Validating dockerfile ...")
        self.validate()
        server_host = input("Host for Docker HUB : ")
        if self.use_confirm:
            print("\n")
            print("The container will be pushed with the following credentials :")
            print(f"Internal Name : {self.lock.module.internal_name.get()}")
            print(f"Version : {self.lock.module.version.get()}")
            print(f'Registry : {server_host}')
            confirm = input("Is the above correct (Y/N) : ")
            if confirm.strip().lower() != 'y':
                sys.exit(0)
        container_name = self.container.name()
        full_container_name = f'{server_host}/{container_name}'
        print("Running Container Build...")
        self.run_build()
        print("Retagging Container ...")
        print(f"{container_name} -> {full_container_name}")
        subprocess.run([
            "docker", "tag", container_name, full_container_name
        ]).check_returncode()
        print(f"Pushing Container ...")
        subprocess.run([
            "docker", "push", full_container_name
        ]).check_returncode()
