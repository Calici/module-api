import unittest
from .timer import Timer
import time

class TimerTest(unittest.TestCase):
    def assert_timer_float(self, timers : dict):
        for k, v in timers.items():
            if isinstance(v, dict):
                assert self .assert_timer_float(v)
            else: self.assertEqual(type(v), float)
        return True

    def test_start_end_timer(self):
        timer   = Timer()
        timer.start('A')
        timer.end('A')
        self.assert_timer_float(timer.timers)
    
    def test_start_end_multi_timer(self):
        timer   = Timer()
        timer.start('A')
        timer.start('B')
        timer.end('A')
        timer.end('B')
        self.assert_timer_float(timer.timers)
    
    def test_start_timer_that_already_exist(self):
        timer   = Timer()
        timer.start('A')
        try:
            timer.start('A')
        except KeyError: return
        assert 'A' == 'Already Exist'
    
    def test_close_closed_timer(self):
        timer   = Timer()
        timer.start('A')
        timer.end('A')
        try:
            timer.end('A')
        except KeyError: return 
        assert 'A' == 'Already Ended'
    
    def test_sum_all_timer(self):
        timer   = Timer()
        timer.start('A')
        timer.end('A')
        timer.sum()
        
    def test_use_with_pattern(self):
        timer = Timer()
        with timer.start('A'):
            time.sleep(1)
        elapsed_time = timer.get_time('A')
        self.assertAlmostEqual(elapsed_time, 1, 1)