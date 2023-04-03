import requests
import json
import pathlib
from typing import List, Union

class HttpException(Exception):
    def __init__(self, status : int, msg : Union[dict, str]):
        self.status     = status
        self.msg        = msg

    def __repr__(self) -> str:
        code    = self.status
        msg     = self.msg
        return "HTTP {code} Error : {msg}".format(code = code, msg = msg)

    def __str__(self) -> str:
        return self.__repr__()

class Http500(HttpException):
    def __init__(self, msg : Union[dict, str]):
        super().__init__(500, msg)

class Http400(HttpException):
    def __init__(self, msg : Union[dict, str]):
        super().__init__(400, msg)

class Server:
    @staticmethod
    def send_command(
        endpoint : str, command : List[str], lock : pathlib.Path,
        auto_gpu : bool = True, 
        gpus : List[int] = [],
        is_manage_for_kill : bool =False,
        module_id : int = -1
    ) -> requests.Response:
        """
            Sends a command to the WSGI server. 
            endpoint -> the server endpoint to use, 
            command -> the command in a list, will be combined with spaces
            lock -> path to the lockfile
            auto_gpu -> automatically assign GPU devices. 
            gpus -> if auto_gpu is false, gpus will be used to assign GPUs 
            is_manage_for_kill -> using kill aidock, add to NoManager
            module_id
        """    
        data = {
            'command'   : command,
            'lock'      : str(lock),
            'auto_gpu'  : auto_gpu,
            'gpus'      : gpus,
            'is_manage_for_kill': is_manage_for_kill,
        }
        if module_id != -1: data['module_id'] = module_id
        response    = Server._send_request(endpoint, data)
        return Server._err_handler(response)
    @staticmethod
    def send_command_with_manager(
        endpoint : str, 
        command : List[str], 
        lock : pathlib.Path,
        auto_gpu : bool = True, 
        gpus : List[int] = [], 
        module_id : int = -1
    ) -> requests.Response:
        """
            Sends a command to the WSGI server and manages the process. 
            endpoint -> the server endpoint to use, 
            command -> the command in a list, will be combined with spaces
            lock -> path to the lockfile
            auto_gpu -> automatically assign GPU devices. 
            gpus -> if auto_gpu is false, gpus will be used to assign GPUs       
            module_id
        """
        response    = Server._send_request(endpoint, {
            'command' : command, 'manage' : True, 'lock' : str(lock),
            'auto_gpu' : auto_gpu, 'gpus' : gpus, 'module_id' : module_id
        })
        return Server._err_handler(response)

    @staticmethod
    def _send_request(endpoint : str, json : dict) -> requests.Response:
        """
            Sends a request to the given endpoint and payload json
        """
        return requests.post(endpoint, json = json)
    @staticmethod
    def _err_handler(resp : requests.Response) -> requests.Response:
        """
            Handle errors from resp
        """
        if resp.status_code == 200: return resp
        elif resp.status_code == 400:
            try:
                raise Http400(resp.json()['error'])
            except json.JSONDecodeError:
                raise Http400(resp.text)
        elif resp.status_code == 500:
            try:
                raise Http500(resp.json()['error'])
            except json.JSONDecodeError:
                raise Http500(resp.text)
        else:
            try:
                raise HttpException(resp.status_code, resp.json()['error'])
            except json.JSONDecodeError:
                raise HttpException(resp.status_code, resp.text)