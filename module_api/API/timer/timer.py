import time
import logging
# TIMER
# start(timer_name : str) -> start a timer with name timer_name
# end(timer_name : str) -> end a timer with name timer_name
# remove(timer_name : str) -> remove a timer with name timer_name
# get_time(timer_name : str) -> get the time delta for timer timer_name
# sum() -> get the total time
class Timer:
    def __init__(self): 
        self.timers     = {}
    def start(self, timer_name : str): 
        try:
            lol     = self.timers[timer_name]
            raise ValueError(f'{timer_name} exists')
        except KeyError:
            self.timers[timer_name]     = {
                'start' : time.time(), 'end' : None
            }

    def _get_delta(self, timer_name : str) -> float: 
        try:
            return self.timers[timer_name]['delta']
        except KeyError:
            start_time  = self.timers[timer_name]['start']
            end_time    = self.timers[timer_name]['end']
            self.timers[timer_name]['delta'] = end_time - start_time
            return self.timers  [timer_name]['delta']

    def end(self, timer_name : str) -> float:
        try:
            if self.timers[timer_name]['end'] is not None: 
                raise ValueError(f'Timer {timer_name} already ended')
            self.timers[timer_name]['end']  = time.time()
            return self._get_delta(timer_name)
        except KeyError: raise KeyError(f"No such timer {timer_name}")
    
    def get_time(self, timer_name : str) -> float:
        try:
            return self._get_delta(timer_name)
        except KeyError:
            raise KeyError(f'No such timer {timer_name} or timer not ended')
    
    def sum(self) -> float:
        return sum([
            v.get('delta') if v['delta'] is not None else 0 for k, v in self.timers.items()
        ])

    def remove(self, timer_name : str) -> float:
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
                