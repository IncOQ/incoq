# Q1 : {(a,) for (a, a_2) in REL(S) if (a == a_2)} : {(Number)}
# Q2 : {(v,) for (v,) in REL(R_Q1) if (v > 1)} : {(Bottom)}
from incoq.mars.runtime import *
# R_Q1 : {(Number)}
R_Q1 = CSet()
# R_Q2 : {(Bottom)}
R_Q2 = Set()
def _maint_R_Q2_for_R_Q1_add(_elem):
    (_v4_v,) = _elem
    if (_v4_v > 1):
        _v4_result = (_v4_v,)
        R_Q2.add(_v4_result)

def _maint_R_Q2_for_R_Q1_remove(_elem):
    (_v5_v,) = _elem
    if (_v5_v > 1):
        _v5_result = (_v5_v,)
        R_Q2.remove(_v5_result)

def _maint_R_Q1_for_S_add(_elem):
    (_v2_a, _v2_a_2) = _elem
    if (_v2_a == _v2_a_2):
        _v2_result = (_v2_a,)
        if (_v2_result not in R_Q1):
            R_Q1.add(_v2_result)
            _maint_R_Q2_for_R_Q1_add(_v2_result)
        else:
            R_Q1.inccount(_v2_result)

def main():
    for (x, y) in [(1, 1), (1, 2), (2, 2), (2, 3)]:
        _v1 = (x, y)
        _maint_R_Q1_for_S_add(_v1)
    print(sorted(R_Q2))

if (__name__ == '__main__'):
    main()
