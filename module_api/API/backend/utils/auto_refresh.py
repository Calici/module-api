import module_api.API.lock as lock
from module_api.API.backend.constants import \
    API_SENDING_TIMEOUT
from .decorator import backend_api_call
import requests
import logging
from typing_extensions import \
    Dict, \
    Any

class RequestAutoRefresh(lock.LockSection):
    def __init__(self, endpoint : str, header : dict):
        super().__init__()
        self._header = header
        self._endpoint = endpoint

    def query(self) -> bool:
        """
            Performs query to retrieve Class data from the backend
        """
        try:
            data = self.__get_data().json()
            self.set_value(data, False)
            return True
        except Exception as e:
            logging.error(str(e))
            return False
    
    def set(self, **kwargs):
        super().set(**kwargs)
        self.__update_backend()
    
    # Private Methods
    @backend_api_call(retry_count = 5)
    def __get_data(self, 
        timeout : int = API_SENDING_TIMEOUT
) -> requests.Response:
        return requests.get(
            url = self._endpoint, 
            headers = self._header,
            timeout = timeout
        )
    @backend_api_call(retry_count = 5)
    def __update_data(self, 
        data : Dict[str, Any], timeout : int = API_SENDING_TIMEOUT
    ) -> requests.Response:
        return requests.post(
            url = self._endpoint, 
            headers = self._header, 
            json = data, 
            timeout = timeout
        )
    
    def __update_backend(self):
        build_dict = self.serialize_changes()
        if build_dict == {}: return
        response = self.__update_data(build_dict).json()
        self.set_value(response, False)
        self.flush()