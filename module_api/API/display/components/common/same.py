from typing import \
  Literal, \
  List
import module_api.API.lock as Lock

def ZoomableField():
  return Lock.LockField[Literal['none', 'normal', 'admet']](str, 'none')

def Messages(
  default : List[str] = [], 
  optimize_merge : bool = False
):
  return Lock.ListField(
    Lock.TypeField(Lock.LockField, str), default, 
    optimize_merge = optimize_merge
  )

class ControlConfig(Lock.LockSection):
    show_run = Lock.LockField(type = bool, default = True)
    show_stop = Lock.LockField(type = bool, default = True)

DisplayStatus = Literal['INIT', 'COMPLETE', 'STOP', 'RUNNING']