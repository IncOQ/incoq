# Q : a -> {(b,) for (a, b) in REL(S)} : {(Number, Number)}
from incoq.mars.runtime import *
# S : {(Number, Number)}
S = Set()
# R_Q : {(Number, Number)}
R_Q = CSet()
# R_Q_bu : {(Number): {(Number)}}
R_Q_bu = Map()
def _maint_R_Q_bu_for_R_Q_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v4_key = (_elem_v1,)
    _v4_value = (_elem_v2,)
    if (_v4_key not in R_Q_bu):
        _v5 = Set()
        R_Q_bu[_v4_key] = _v5
    R_Q_bu[_v4_key].add(_v4_value)

def _maint_R_Q_bu_for_R_Q_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v6_key = (_elem_v1,)
    _v6_value = (_elem_v2,)
    R_Q_bu[_v6_key].remove(_v6_value)
    if (len(R_Q_bu[_v6_key]) == 0):
        del R_Q_bu[_v6_key]

def _maint_R_Q_for_S_add(_elem):
    (_v2_a, _v2_b) = _elem
    _v2_result = (_v2_a, _v2_b)
    if (_v2_result not in R_Q):
        R_Q.add(_v2_result)
        _maint_R_Q_bu_for_R_Q_add(_v2_result)
    else:
        R_Q.inccount(_v2_result)

def _maint_R_Q_for_S_remove(_elem):
    (_v3_a, _v3_b) = _elem
    _v3_result = (_v3_a, _v3_b)
    if (R_Q.getcount(_v3_result) == 1):
        _maint_R_Q_bu_for_R_Q_remove(_v3_result)
        R_Q.remove(_v3_result)
    else:
        R_Q.deccount(_v3_result)

def main():
    for (x, y) in [(1, 2), (2, 3), (3, 4)]:
        _v1 = (x, y)
        S.add(_v1)
        _maint_R_Q_for_S_add(_v1)
    a = 1
    print(R_Q_bu.get((a,), Set()).unwrap())

if (__name__ == '__main__'):
    main()
