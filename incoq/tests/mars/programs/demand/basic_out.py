# Q : {(c,) for (a, b) in REL(S) for (b, c) in REL(S)} : {(Number)}
# Q_T_b_1 : {(b,) for (a, b) in REL(S)} : Bottom
# Q_dS : {(b, c) for (b,) in REL(R_Q_T_b_1) for (b, c) in REL(S)} : Bottom
from incoq.mars.runtime import *
# S : {(Number, Number)}
S = Set()
# R_Q : {(Number)}
R_Q = CSet()
# R_Q_T_b_1 : Bottom
R_Q_T_b_1 = CSet()
# R_Q_dS : Bottom
R_Q_dS = Set()
# R_Q_unwrapped : {Number}
R_Q_unwrapped = Set()
# S_bu : {Number: {Number}}
S_bu = Map()
# R_Q_dS_bu : {Bottom: {Bottom}}
R_Q_dS_bu = Map()
# S_ub : {Number: {Number}}
S_ub = Map()
def _maint_S_bu_for_S_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v10_key = _elem_v1
    _v10_value = _elem_v2
    if (_v10_key not in S_bu):
        _v11 = Set()
        S_bu[_v10_key] = _v11
    S_bu[_v10_key].add(_v10_value)

def _maint_S_bu_for_S_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v12_key = _elem_v1
    _v12_value = _elem_v2
    S_bu[_v12_key].remove(_v12_value)
    if (len(S_bu[_v12_key]) == 0):
        del S_bu[_v12_key]

def _maint_S_ub_for_S_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v13_key = _elem_v2
    _v13_value = _elem_v1
    if (_v13_key not in S_ub):
        _v14 = Set()
        S_ub[_v13_key] = _v14
    S_ub[_v13_key].add(_v13_value)

def _maint_S_ub_for_S_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v15_key = _elem_v2
    _v15_value = _elem_v1
    S_ub[_v15_key].remove(_v15_value)
    if (len(S_ub[_v15_key]) == 0):
        del S_ub[_v15_key]

def _maint_R_Q_dS_bu_for_R_Q_dS_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v16_key = _elem_v1
    _v16_value = _elem_v2
    if (_v16_key not in R_Q_dS_bu):
        _v17 = Set()
        R_Q_dS_bu[_v16_key] = _v17
    R_Q_dS_bu[_v16_key].add(_v16_value)

def _maint_R_Q_dS_bu_for_R_Q_dS_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v18_key = _elem_v1
    _v18_value = _elem_v2
    R_Q_dS_bu[_v18_key].remove(_v18_value)
    if (len(R_Q_dS_bu[_v18_key]) == 0):
        del R_Q_dS_bu[_v18_key]

def _maint_R_Q_unwrapped_for_R_Q_add(_elem):
    _v19_v = index(_elem, 0)
    R_Q_unwrapped.add(_v19_v)

def _maint_R_Q_unwrapped_for_R_Q_remove(_elem):
    _v20_v = index(_elem, 0)
    R_Q_unwrapped.remove(_v20_v)

def _maint_R_Q_dS_for_R_Q_T_b_1_add(_elem):
    # Cost: O(S_bu)
    (_v6_b,) = _elem
    for _v6_c in (S_bu[_v6_b] if (_v6_b in S_bu) else ()):
        _v6_result = (_v6_b, _v6_c)
        R_Q_dS.add(_v6_result)
        _maint_R_Q_dS_bu_for_R_Q_dS_add(_v6_result)

def _maint_R_Q_dS_for_R_Q_T_b_1_remove(_elem):
    # Cost: O(S_bu)
    (_v7_b,) = _elem
    for _v7_c in (S_bu[_v7_b] if (_v7_b in S_bu) else ()):
        _v7_result = (_v7_b, _v7_c)
        _maint_R_Q_dS_bu_for_R_Q_dS_remove(_v7_result)
        R_Q_dS.remove(_v7_result)

def _maint_R_Q_dS_for_S_add(_elem):
    # Cost: O(1)
    (_v8_b, _v8_c) = _elem
    if ((_v8_b,) in R_Q_T_b_1):
        _v8_result = (_v8_b, _v8_c)
        R_Q_dS.add(_v8_result)
        _maint_R_Q_dS_bu_for_R_Q_dS_add(_v8_result)

def _maint_R_Q_dS_for_S_remove(_elem):
    # Cost: O(1)
    (_v9_b, _v9_c) = _elem
    if ((_v9_b,) in R_Q_T_b_1):
        _v9_result = (_v9_b, _v9_c)
        _maint_R_Q_dS_bu_for_R_Q_dS_remove(_v9_result)
        R_Q_dS.remove(_v9_result)

def _maint_R_Q_T_b_1_for_S_add(_elem):
    # Cost: O(S_bu)
    (_v4_a, _v4_b) = _elem
    _v4_result = (_v4_b,)
    if (_v4_result not in R_Q_T_b_1):
        R_Q_T_b_1.add(_v4_result)
        _maint_R_Q_dS_for_R_Q_T_b_1_add(_v4_result)
    else:
        R_Q_T_b_1.inccount(_v4_result)

def _maint_R_Q_T_b_1_for_S_remove(_elem):
    # Cost: O(S_bu)
    (_v5_a, _v5_b) = _elem
    _v5_result = (_v5_b,)
    if (R_Q_T_b_1.getcount(_v5_result) == 1):
        _maint_R_Q_dS_for_R_Q_T_b_1_remove(_v5_result)
        R_Q_T_b_1.remove(_v5_result)
    else:
        R_Q_T_b_1.deccount(_v5_result)

def _maint_R_Q_for_S_add(_elem):
    # Cost: O((R_Q_dS_bu + S_ub))
    (_v2_a, _v2_b) = _elem
    if ((_v2_a, _v2_b) in S):
        for _v2_c in (R_Q_dS_bu[_v2_b] if (_v2_b in R_Q_dS_bu) else ()):
            _v2_result = (_v2_c,)
            if (_v2_result not in R_Q):
                R_Q.add(_v2_result)
                _maint_R_Q_unwrapped_for_R_Q_add(_v2_result)
            else:
                R_Q.inccount(_v2_result)
    (_v2_b, _v2_c) = _elem
    if ((_v2_b, _v2_c) in R_Q_dS):
        for _v2_a in (S_ub[_v2_b] if (_v2_b in S_ub) else ()):
            _v2_result = (_v2_c,)
            if (_v2_result not in R_Q):
                R_Q.add(_v2_result)
                _maint_R_Q_unwrapped_for_R_Q_add(_v2_result)
            else:
                R_Q.inccount(_v2_result)

def _maint_R_Q_for_S_remove(_elem):
    # Cost: O((R_Q_dS_bu + S_ub))
    (_v3_a, _v3_b) = _elem
    if ((_v3_a, _v3_b) in S):
        for _v3_c in (R_Q_dS_bu[_v3_b] if (_v3_b in R_Q_dS_bu) else ()):
            _v3_result = (_v3_c,)
            if (R_Q.getcount(_v3_result) == 1):
                _maint_R_Q_unwrapped_for_R_Q_remove(_v3_result)
                R_Q.remove(_v3_result)
            else:
                R_Q.deccount(_v3_result)
    (_v3_b, _v3_c) = _elem
    if ((_v3_b, _v3_c) in R_Q_dS):
        for _v3_a in (S_ub[_v3_b] if (_v3_b in S_ub) else ()):
            _v3_result = (_v3_c,)
            if (R_Q.getcount(_v3_result) == 1):
                _maint_R_Q_unwrapped_for_R_Q_remove(_v3_result)
                R_Q.remove(_v3_result)
            else:
                R_Q.deccount(_v3_result)

def main():
    for (x, y) in [(1, 2), (1, 3), (2, 3), (2, 4)]:
        _v1 = (x, y)
        S.add(_v1)
        _maint_S_bu_for_S_add(_v1)
        _maint_S_ub_for_S_add(_v1)
        _maint_R_Q_dS_for_S_add(_v1)
        _maint_R_Q_T_b_1_for_S_add(_v1)
        _maint_R_Q_for_S_add(_v1)
    print(sorted(R_Q_unwrapped))

if (__name__ == '__main__'):
    main()
