import threading
from multiprocessing import Process
from typing_extensions import List

def split_array(arr:List, num:int=None, size:int=1, b_order = False):
    # sourcery skip: extract-method, remove-unnecessary-else
    """Split array by size

    Args:
        arr ([type]): [description]
        size (int, optional): Defaults to 1. Number of children arr.
        num ([int], optional): Defaults to None. Size of children.
        b_order ([bool], optional): Defaults to False. []
    Raises:
        AssertionError: [description]

    Returns:
        [type]: [description]
    """
    if not arr:
        return []
    length = len(arr)
    if num:
        if num < 1:
            raise AssertionError("Num is < 1")
        num = min(num, length)
        if not b_order:
            mod = length % num
            size = length // num
            size_1 = size + 1
            ret = [arr[i:i + size_1] for i in range(0, mod*size_1, size_1)]
            arr = arr[mod * size_1:]
            length = len(arr)
            ret.extend([arr[i:i + size] for i in range(0, length, size)])
        else:
            ret = [[] for _ in range(num)]
            for i, v in enumerate(arr):
                ret[i % num].append(v)
        return ret
    else:
        if size < 1:
            raise AssertionError("Size is < 1")

        return [arr[i:i + size] for i in range(0, length, size)]


def thread_execute(*args, thread_num=5, func=None, list_arr=None, b_lock=False, b_split_arr=True):
    """Execute by threads

    Args:
        thread_num (int, optional): Number of threads. Defaults to 5.
        func ([function], optional): Function execute. Function must has arg item, item is item in list_arr
        list_arr (list): list_arr
        b_lock ([bool], optional): Default to False, using threading.Lock()
        b_split_arr ([bool], optional): Default to True, split list_arr or not
    """
    class OtherLocalThread(threading.Thread):
        """Thread job"""

        def __init__(self, *args, items=None, func=None, lock=None):
            """Init

            Args:
                file_list (list[dict]): Description
            """
            threading.Thread.__init__(self)
            self.func = func
            self.args = args
            self.items = items
            self.lock = lock

        def run(self):
            """Running"""
            if self.func and self.items:
                for _ in self.items:
                    try:
                        if self.lock:
                            self.func(*self.args, item=_, lock=self.lock)
                        else:
                            self.func(*self.args, item=_)
                    except Exception as ex:
                        raise ex

    if thread_num < 1:
        raise AssertionError("thread_num is < 1")
    if not func:
        raise AssertionError("func parameter is None.")
    if not list_arr:
        raise AssertionError("list_arr parameter is None or empty.")

    lock = threading.Lock() if b_lock else None
    list_arr_splited = split_array(list_arr, num=thread_num) if b_split_arr else list_arr

    list_thread = []
    for _ in list_arr_splited:
        thread = OtherLocalThread(*args, items=_, func=func, lock=lock)
        thread.start()
        list_thread.append(thread)

    # Wait until all threads have finished
    for _ in list_thread:
        _.join()


def multi_process_execute(*args, process_num=5, func=None, list_arr=None):

    def process_of_thread(*args, func=None, items=None):
        if not items or not func:
            return

        for item in items:
            func(*args, item=item)

    if process_num < 1:
        raise AssertionError("process_num is < 1")
    if not func:
        raise AssertionError("func parameter is None.")
    if not list_arr:
        raise AssertionError("items parameter is None or empty.")

    list_arr_splited = split_array(list_arr, num=process_num)
    list_processes = []
    for v in list_arr_splited:
        p = Process(args=args, kwargs={'items': v, 'func': func}, target=process_of_thread)
        list_processes.append(p)
        p.start()

    # completing process
    for p in list_processes:
        p.join()
