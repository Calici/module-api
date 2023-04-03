# Library Imports
import requests
import logging
import API.lock as lock

# An exception thrown when there is an error with the request
## Thrown mainly when the correct status code is returned
class RequestError(Exception):
    def __init__(self, obj : requests.Response):
        self._obj   = obj
    def obj(self): return self._obj

# Auto refreshes data to make sure that the latest data is always
# used. Asset here will be used as the structure. 
class RequestAutoRefresh(lock.LockSection):
    def __init__(self, endpoint : str, header : dict):
        super().__init__()
        self._header    = header
        self._endpoint  = endpoint
        self.query()

    def update_header(self, new_header : dict):
        self._header    = new_header

    def query(self):
        resp    = self._query_data()
        self._set_value(resp, False)
    # Query data from the backend
    def _query_data(self) -> dict:
        resp    = requests.get(
            url = self._endpoint, headers = self._header
        )
        if resp.status_code != 200: raise RequestError(resp)
        return resp.json()
    
    def set(self, **kwargs):
        super().set(**kwargs)
        self._update_changes()

    def _update_changes(self):
        # Build dictionary
        build_dict  = self.serialize_changes()
        # Block update if empty dictionary
        if build_dict == {}: return
        # Update data
        try:
            conf    = self._update_data(build_dict)
            self._set_value(conf, False)
            self.flush()
        except RequestError as e:
            logging.error(
                f'Fail with {e.obj().status_code}, changes, saved'
            )

    # Update data in the backend
    def _update_data(self, data : dict)  -> dict:
        resp    = requests.post(
            url = self._endpoint, headers = self._header, json = data
        )
        if resp.status_code != 200: raise RequestError(resp)
        return resp.json()