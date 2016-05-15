# Q : a -> {(a, b) for (a, b) in REL(S)} : {(Number, Number)}
from incoq.runtime import *
# R_Q_bu : {Number: {(Number)}}
R_Q_bu = Map()
def _maint_R_Q_bu_for_R_Q_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v4_key = _elem_v1
    _v4_value = (_elem_v2,)
    if (_v4_key not in R_Q_bu):
        _v5 = Set()
        R_Q_bu[_v4_key] = _v5
    R_Q_bu[_v4_key].add(_v4_value)

def _maint_R_Q_bu_for_R_Q_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v6_key = _elem_v1
    _v6_value = (_elem_v2,)
    R_Q_bu[_v6_key].remove(_v6_value)
    if (len(R_Q_bu[_v6_key]) == 0):
        del R_Q_bu[_v6_key]

def _maint_R_Q_for_S_add(_elem):
    (_v2_a, _v2_b) = _elem
    _v2_result = (_v2_a, _v2_b)
    _maint_R_Q_bu_for_R_Q_add(_v2_result)

def main():
    for (x, y) in [(1, 2), (2, 3), (3, 4)]:
        _v1 = (x, y)
        _maint_R_Q_for_S_add(_v1)
    a = 1
    print(sorted((R_Q_bu[a] if (a in R_Q_bu) else Set())))
    R_Q_bu.dictclear()
    print(sorted((R_Q_bu[a] if (a in R_Q_bu) else Set())))

if (__name__ == '__main__'):
    main()
