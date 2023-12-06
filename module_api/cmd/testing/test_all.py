from module_api.cmd.base import \
    ModuleLock, \
    Container, \
    Cleaner
from .base import \
    TestBase, \
    SERVER_FILE
from module_api.API.test import random_string
import subprocess

class TestAll(TestBase):
    def __init__(self, lock : ModuleLock):
        super().__init__(lock)
        self.container = Container(lock)
        self.prepare_run()

    def get_api_token(self) -> str:
        try:
            return self.api_token
        except AttributeError:
            self.api_token = random_string(20)
            return self.api_token
    
    def prep_test(self) -> subprocess.Popen:
        subprocess.run(["docker", "network", "create", self.network_name()])
        process = subprocess.Popen([
            "docker", "run",
            "--rm", "--name", self.server_name(),
            "--network", self.network_name(),
            "-v", "{0}:{1}".format(str(SERVER_FILE),'/app/server.py'),
            "-e", f"PORT={self.port()}",
            "python:3.11-slim", 
            "python3",
            "/app/server.py"
        ])
        return process

    def cleanup_test(self, process : subprocess.Popen):
        process.kill()
        process.wait()
        subprocess.run(["docker", "kill", self.server_name()])
        subprocess.run(["docker", "network", "rm", self.network_name()])
    
    def server_name(self):
        try:
            return self.__server_name
        except AttributeError:
            self.__server_name = random_string(10)
            return self.__server_name

    def network_name(self):
        try:
            return self.__network_name
        except AttributeError:
            self.__network_name = random_string(10)
            return self.__network_name

    def port(self) -> int:
        return 65000

    def prepare_run(self):
        port = self.port()
        server_name = self.server_name()
        self.run_args = {
            test.name.get() : [
                *self.container.get_env_args({
                    'DJANGO_API_ENDPOINT' : f'http://{server_name}:{port}',
                    'DJANGO_API_TOKEN' : self.get_api_token()
                }), 
                *self.container.get_volume_args([
                    '{0}:{1}'.format(
                        str(test.path.get()), 
                        str(self.container_root() / test.name.get())
                    )
                ]),
                "--network={0}".format(self.network_name()),
                "--rm", "-it"
            ]
            for test in self.lock.testing.get()
        }

    def run_process(self, name : str):
        process = self.container.run(
            self.run_args[name], 
            ["--lock", f"/data/{name}/workdir/.reserved/default.lock"]
        )
        process.wait()

    def action(self):
        tests = self.lock.testing.get()
        if len(tests) == 0:
            print("No Tests")
            return
        with Cleaner(self.prep_test, self.cleanup_test):
            for test in self.lock.testing.get():
                name = test.name.get()
                print(f"Running test : {name}")
                self.run_process(name)