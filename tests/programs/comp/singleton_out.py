# Q : {(x,) for (x,) in REL(S_wrapped) if (x > 2)} : {(Number)}
from incoq.runtime import *
# R_Q_unwrapped : {Number}
R_Q_unwrapped = Set()
def _maint_R_Q_unwrapped_for_R_Q_add(_elem):
    _v5_v = index(_elem, 0)
    R_Q_unwrapped.add(_v5_v)

def _maint_R_Q_unwrapped_for_R_Q_remove(_elem):
    _v6_v = index(_elem, 0)
    R_Q_unwrapped.remove(_v6_v)

def _maint_R_Q_for_S_wrapped_add(_elem):
    (_v3_x,) = _elem
    if (_v3_x > 2):
        _v3_result = (_v3_x,)
        _maint_R_Q_unwrapped_for_R_Q_add(_v3_result)

def _maint_R_Q_for_S_wrapped_remove(_elem):
    (_v4_x,) = _elem
    if (_v4_x > 2):
        _v4_result = (_v4_x,)
        _maint_R_Q_unwrapped_for_R_Q_remove(_v4_result)

def _maint_S_wrapped_for_S_add(_elem):
    _v1_v = (_elem,)
    _maint_R_Q_for_S_wrapped_add(_v1_v)

def main():
    for a in [1, 2, 3, 4]:
        _maint_S_wrapped_for_S_add(a)
    print(sorted(R_Q_unwrapped))

if (__name__ == '__main__'):
    main()
