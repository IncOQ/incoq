# Q1 : {(a,) for (a, a) in REL(S)} : {(Number)}
# Q2 : {(v,) for (v,) in VARS(R_Q1) if (v > 1)} : {(Number)}
from incoq.mars.runtime import *
# S : {(Number, Number)}
S = Set()
# R_Q1 : {(Number)}
R_Q1 = CSet()
# R_Q2 : {(Number)}
R_Q2 = CSet()
def _maint_R_Q2_for_R_Q1_add(_elem):
    (_v4_v,) = _elem
    if (_v4_v > 1):
        _v4_result = (_v4_v,)
        if (_v4_result not in R_Q2):
            R_Q2.add(_v4_result)
        else:
            R_Q2.inccount(_v4_result)

def _maint_R_Q2_for_R_Q1_remove(_elem):
    (_v5_v,) = _elem
    if (_v5_v > 1):
        _v5_result = (_v5_v,)
        if (R_Q2.getcount(_v5_result) == 1):
            R_Q2.remove(_v5_result)
        else:
            R_Q2.deccount(_v5_result)

def _maint_R_Q1_for_S_add(_elem):
    (_v2_a, _v2_a_2) = _elem
    if (_v2_a == _v2_a_2):
        _v2_result = (_v2_a,)
        if (_v2_result not in R_Q1):
            R_Q1.add(_v2_result)
            _maint_R_Q2_for_R_Q1_add(_v2_result)
        else:
            R_Q1.inccount(_v2_result)

def _maint_R_Q1_for_S_remove(_elem):
    (_v3_a, _v3_a_2) = _elem
    if (_v3_a == _v3_a_2):
        _v3_result = (_v3_a,)
        if (R_Q1.getcount(_v3_result) == 1):
            _maint_R_Q2_for_R_Q1_remove(_v3_result)
            R_Q1.remove(_v3_result)
        else:
            R_Q1.deccount(_v3_result)

def main():
    for (x, y) in [(1, 1), (1, 2), (2, 2), (2, 3)]:
        _v1 = (x, y)
        S.add(_v1)
        _maint_R_Q1_for_S_add(_v1)
    print(sorted(R_Q2.unwrap()))

if (__name__ == '__main__'):
    main()
