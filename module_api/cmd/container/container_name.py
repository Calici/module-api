from module_api.cmd.base import \
    ModuleLock, \
    ActionHandler, \
    Container

class ContainerName(ActionHandler):
    def __init__(self, lock : ModuleLock):
        self.container = Container(lock)
    def action(self):
        print(self.container.name())