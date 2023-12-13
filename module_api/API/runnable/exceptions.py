from typing_extensions import Union
# Stops running of the process
class StopRunnable(Exception):
    def __init__(self, message : str, org_exc : Union[Exception, None] = None):
        super().__init__(message)
        self.message = message
        self.org_exc = org_exc

    def __repr__(self):
        return self.message

class StopRunnableStatusStop(Exception):
    def __init__(self, message : str, org_exc : Union[Exception, None] = None):
        super().__init__(message)
        self.message = message
        self.org_exc = org_exc

    def __repr__(self):
        return self.message

class StopRunnableStatusError(Exception):
    def __init__(self, message : str, org_exc : Union[Exception, None] = None):
        super().__init__(message)
        self.message = message
        self.org_exc = org_exc

    def __repr__(self):
        return self.message
