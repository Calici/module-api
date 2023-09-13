import requests

class RetryError(Exception):
    def __init__(self, obj):
        super().__init__()
        self.obj = None
        self.message = ''
        if isinstance(obj, requests.Response):
            self.obj    = obj
        else:
            self.message = str(obj)
        
    def __str__(self):
        return self.message or str(self.obj)
    
class NoRetryError(Exception):
    def __init__(self, obj : requests.Response):
        super().__init__()
        self.obj = None
        self.message = ''
        if isinstance(obj, requests.Response):
            self.obj    = obj
        else:
            self.message = str(obj)
        
    def __str__(self):
        return self.message or str(self.obj)
        
class APICallError(Exception):
    def __init__(self, msg : str):
        self.msg = msg
    def __str__(self):
        return self.msg