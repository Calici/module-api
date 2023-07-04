from datetime import datetime
import pytz

def get_current_time():
    return datetime.now(tz=pytz.timezone('Asia/Seoul'))

def get_original_time():
    return datetime(1970,1,1,tzinfo=pytz.timezone('Asia/Seoul'))
