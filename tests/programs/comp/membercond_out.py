# Q : {(b,) for (a, b) in REL(S) for (a,) in REL(R)} : {(Number)}
from incoq.runtime import *
# R : {(Number)}
R = Set()
# R_Q : {(Number)}
R_Q = CSet()
# S_bu : {Number: {Number}}
S_bu = Map()
def _maint_S_bu_for_S_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v7_key = _elem_v1
    _v7_value = _elem_v2
    if (_v7_key not in S_bu):
        _v8 = Set()
        S_bu[_v7_key] = _v8
    S_bu[_v7_key].add(_v7_value)

def _maint_R_Q_for_S_add(_elem):
    (_v3_a, _v3_b) = _elem
    if ((_v3_a,) in R):
        _v3_result = (_v3_b,)
        if (_v3_result not in R_Q):
            R_Q.add(_v3_result)
        else:
            R_Q.inccount(_v3_result)

def _maint_R_Q_for_R_add(_elem):
    (_v5_a,) = _elem
    for _v5_b in (S_bu[_v5_a] if (_v5_a in S_bu) else ()):
        _v5_result = (_v5_b,)
        if (_v5_result not in R_Q):
            R_Q.add(_v5_result)
        else:
            R_Q.inccount(_v5_result)

def main():
    for (x, y) in [(1, 2), (1, 3), (2, 3), (2, 4)]:
        _v1 = (x, y)
        _maint_S_bu_for_S_add(_v1)
        _maint_R_Q_for_S_add(_v1)
    _v2 = (1,)
    R.add(_v2)
    _maint_R_Q_for_R_add(_v2)
    print(sorted(R_Q))

if (__name__ == '__main__'):
    main()
