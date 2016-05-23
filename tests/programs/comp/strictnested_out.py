# Q : {(c,) for (a, b, c) in REL(S_flattened)} : {(Number)}
from incoq.runtime import *
# R_Q : {(Number)}
R_Q = CSet()
def _maint_R_Q_for_S_flattened_add(_elem):
    (_v5_a, _v5_b, _v5_c) = _elem
    _v5_result = (_v5_c,)
    if (_v5_result not in R_Q):
        R_Q.add(_v5_result)
    else:
        R_Q.inccount(_v5_result)

def main():
    for x in [1, 2, 3]:
        _v1 = ((x, (x * 10)), (x * 100))
        _v3 = (index(index(_v1, 0), 0), index(index(_v1, 0), 1), index(_v1, 1))
        _maint_R_Q_for_S_flattened_add(_v3)
    print(sorted(R_Q))
    _v2 = ((1, 10), 100)
    _v4 = (index(index(_v2, 0), 0), index(index(_v2, 0), 1), index(_v2, 1))
    _maint_R_Q_for_S_flattened_add(_v4)
    print(sorted(R_Q))
    R_Q.clear()
    print(sorted(R_Q))

if (__name__ == '__main__'):
    main()
