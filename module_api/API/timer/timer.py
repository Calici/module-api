import time
import logging
from typing_extensions import \
    Dict, \
    TypedDict, \
    Union, \
    NotRequired
from module_api.API.patterns import \
    WithPattern
# TIMER
# start(timer_name : str) -> start a timer with name timer_name
# end(timer_name : str) -> end a timer with name timer_name
# remove(timer_name : str) -> remove a timer with name timer_name
# get_time(timer_name : str) -> get the time delta for timer timer_name
# sum() -> get the total time
TimerT = TypedDict("TimerT", {
    "start" : float, 
    "end" : Union[float, None],
    'delta' : NotRequired[float]
})

class Timer:
    def __init__(self): 
        self.timers : Dict[str, TimerT] = {}
    def start(self, timer_name : str) -> WithPattern: 
        if timer_name in self.timers:
            raise KeyError(f'{timer_name} exists')
        self.timers[timer_name] = {
            'start' : time.time(), 'end' : None
        }
        return WithPattern(
            lambda: timer_name,
            lambda name: self.end(name)
        )

    def _get_delta(self, timer_name : str) -> float: 
        try:
            return self.timers[timer_name]['delta']
        except KeyError:
            start_time  = self.timers[timer_name]['start']
            end_time    = self.timers[timer_name]['end']
            if not end_time: 
                raise RuntimeError("end_time is not defined")
            delta = end_time - start_time
            self.timers[timer_name]['delta'] = delta
            return delta

    def end(self, timer_name : str) -> float:
        try:
            if self.timers[timer_name]['end'] is not None: 
                raise KeyError(f'Timer {timer_name} already ended')
            self.timers[timer_name]['end']  = time.time()
            return self._get_delta(timer_name)
        except KeyError: raise KeyError(f"No such timer {timer_name}")
    
    def get_time(self, timer_name : str) -> float:
        try:
            return self._get_delta(timer_name)
        except KeyError:
            raise KeyError(f'No such timer {timer_name} or timer not ended')
    
    def sum(self) -> float:
        return sum([ v.get('delta', 0) for k, v in self.timers.items() ])

    def remove(self, timer_name : str):
        try: 
            self.timers.pop(timer_name)
        except KeyError: 
            raise KeyError(f'No such timer {timer_name}')
        
    def log_all(self, logger=None):
        total_time  = self.sum()
        log = logger if logger is not None else logging
        log.info("Elapsed times in seconds")
        log.info(f'Total time : {total_time}')
        for k, v in self.timers.items():
            log.info(f'{k} : {v.get("delta", "Timer not ended")}')
                