# Q : count(S) : Number
from incoq.mars.runtime import *
# S : {(Number)}
S = Set()
# A_Q : {(): Number}
A_Q = Map()
def _maint_A_Q_for_S_add(_elem):
    (_elem_v1,) = _elem
    _v3_key = ()
    _v3_value = (_elem_v1,)
    _v3_state = A_Q.get(_v3_key, 0)
    _v3_state = (_v3_state + 1)
    if (_v3_key in A_Q):
        del A_Q[_v3_key]
    A_Q[_v3_key] = _v3_state

def _maint_A_Q_for_S_remove(_elem):
    (_elem_v1,) = _elem
    _v4_key = ()
    _v4_value = (_elem_v1,)
    _v4_state = A_Q[_v4_key]
    _v4_state = (_v4_state - 1)
    del A_Q[_v4_key]
    if (not (_v4_state == 0)):
        A_Q[_v4_key] = _v4_state

def main():
    for x in [1, 2, 3, 4]:
        _v1 = (x,)
        S.add(_v1)
        _maint_A_Q_for_S_add(_v1)
    print(A_Q.get((), 0))
    _v2 = (4,)
    _maint_A_Q_for_S_remove(_v2)
    S.remove(_v2)
    print(A_Q.get((), 0))
    print(A_Q.get((), 0))

if (__name__ == '__main__'):
    main()
