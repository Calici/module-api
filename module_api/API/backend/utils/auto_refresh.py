# Library Imports
import requests
import logging
from time import sleep

# Local import
import API.lock as lock
from .decorator import api_to_django_execute, RetryError, NoRetryError
from module_api.API.backend.constants import WAITING_FOR_ERROR_API_SENDING, API_SENDING_TIMEOUT

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
        try:
            resp    = self._query_data().json()
            self._set_value(resp, False)
            return True
        except RetryError as ex:
            logging.error(f'Module.query - Fail with {str(ex)}, changes, saved')
        except NoRetryError as ex:
            logging.error(f'Module.query - Fail with {str(ex)}, changes, saved')
        except Exception as ex:
            logging.error(f"Module.query - {ex}")
        return False

    # Query data from the backend
    @api_to_django_execute
    def _query_data(self, timeout=API_SENDING_TIMEOUT) -> dict:
        return requests.get(
            url = self._endpoint, headers = self._header, timeout=timeout
        )

    def set(self, **kwargs):
        retry_count = kwargs.pop('retry_count', 1)
        retry_count = max(retry_count, 1)
        super().set(**kwargs)
        return self._update_changes(retry_count = retry_count)

    def _update_changes(self, retry_count: int = 1):
        # Build dictionary
        build_dict  = self.serialize_changes()
        # Block update if empty dictionary
        if build_dict == {}: return True
        # Update data
        while retry_count > 0:
            try:
                conf    = self._update_data(build_dict).json()
                retry_count = 0
                self._set_value(conf, False)
                self.flush()
                return True
            except RetryError as ex:
                logging.error(f'Module.update - Fail with {str(ex)}')
                if retry_count > 0:
                    retry_count -= 1
                    sleep(WAITING_FOR_ERROR_API_SENDING)    # sleep 5 seconds
            except NoRetryError as ex:
                retry_count = 0
                logging.error(f'Module.update - Fail with {str(ex)}')
            except Exception as ex:
                retry_count = 0
                logging.error(f'Module.update - Fail with {str(ex)}')
        return False
        
    # Update data in the backend
    @api_to_django_execute
    def _update_data(self, data : dict, timeout=API_SENDING_TIMEOUT)  -> dict:
        return requests.post(
            url = self._endpoint, headers = self._header, json = data, timeout=timeout
        )
        # if resp.status_code != 200: raise RequestError(resp)
        # return resp.json()