PROCESS_REFRESH_TIME_OVER = 2*60 # 2 mins, if last_check over it, zombie
PROCESS_REFRESH_TIME = 1*60 # 1 mins, if last_check overt it and process.status == RUNNING and process is controlled in Manager -> update last_check
API_SENDING_TIMEOUT = 5 # 5 seconds
WAITING_FOR_ERROR_API_SENDING = 5 # 5 seconds
SEND_API_RETRY_COUNT_WHEN_STOP = 5 # 120 * 5 = 10 mins
SEND_API_RETRY_COUNT_WHEN_COMPLETE = 10 # 120 * 5 = 10 mins