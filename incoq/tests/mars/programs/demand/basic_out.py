# Q : {(c,) for (a, b) in REL(S) for (b, c) in REL(S)} : {(Number)}
# Q_T_a : {(a,) for (a, b) in REL(S)} : Bottom
# Q_T_b_1 : {(b,) for (a, b) in REL(S)} : Bottom
# Q_dS : {(b, c) for (b, c) in REL(S)} : Bottom
# Q_T_b_2 : {(b,) for (b, c) in REL(R_Q_dS)} : Bottom
# Q_T_c : {(c,) for (b, c) in REL(R_Q_dS)} : Bottom
from incoq.mars.runtime import *
# S : {(Number, Number)}
S = Set()
# R_Q : {(Number)}
R_Q = CSet()
# R_Q_T_a : Bottom
R_Q_T_a = CSet()
# R_Q_T_b_1 : Bottom
R_Q_T_b_1 = CSet()
# R_Q_dS : Bottom
R_Q_dS = CSet()
# R_Q_T_b_2 : Bottom
R_Q_T_b_2 = CSet()
# R_Q_T_c : Bottom
R_Q_T_c = CSet()
# R_Q_dS_bu : {(Bottom): {(Bottom)}}
R_Q_dS_bu = Map()
# S_ub : {(Number): {(Number)}}
S_ub = Map()
def _maint_R_Q_dS_bu_for_R_Q_dS_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v14_key = (_elem_v1,)
    _v14_value = (_elem_v2,)
    if (_v14_key not in R_Q_dS_bu):
        _v15 = Set()
        R_Q_dS_bu[_v14_key] = _v15
    R_Q_dS_bu[_v14_key].add(_v14_value)

def _maint_R_Q_dS_bu_for_R_Q_dS_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v16_key = (_elem_v1,)
    _v16_value = (_elem_v2,)
    R_Q_dS_bu[_v16_key].remove(_v16_value)
    if (len(R_Q_dS_bu[_v16_key]) == 0):
        del R_Q_dS_bu[_v16_key]

def _maint_S_ub_for_S_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v17_key = (_elem_v2,)
    _v17_value = (_elem_v1,)
    if (_v17_key not in S_ub):
        _v18 = Set()
        S_ub[_v17_key] = _v18
    S_ub[_v17_key].add(_v17_value)

def _maint_S_ub_for_S_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v19_key = (_elem_v2,)
    _v19_value = (_elem_v1,)
    S_ub[_v19_key].remove(_v19_value)
    if (len(S_ub[_v19_key]) == 0):
        del S_ub[_v19_key]

def _maint_R_Q_T_c_for_R_Q_dS_add(_elem):
    (_v12_b, _v12_c) = _elem
    _v12_result = (_v12_c,)
    if (_v12_result not in R_Q_T_c):
        R_Q_T_c.add(_v12_result)
    else:
        R_Q_T_c.inccount(_v12_result)

def _maint_R_Q_T_c_for_R_Q_dS_remove(_elem):
    (_v13_b, _v13_c) = _elem
    _v13_result = (_v13_c,)
    if (R_Q_T_c.getcount(_v13_result) == 1):
        R_Q_T_c.remove(_v13_result)
    else:
        R_Q_T_c.deccount(_v13_result)

def _maint_R_Q_T_b_2_for_R_Q_dS_add(_elem):
    (_v10_b, _v10_c) = _elem
    _v10_result = (_v10_b,)
    if (_v10_result not in R_Q_T_b_2):
        R_Q_T_b_2.add(_v10_result)
    else:
        R_Q_T_b_2.inccount(_v10_result)

def _maint_R_Q_T_b_2_for_R_Q_dS_remove(_elem):
    (_v11_b, _v11_c) = _elem
    _v11_result = (_v11_b,)
    if (R_Q_T_b_2.getcount(_v11_result) == 1):
        R_Q_T_b_2.remove(_v11_result)
    else:
        R_Q_T_b_2.deccount(_v11_result)

def _maint_R_Q_dS_for_S_add(_elem):
    (_v8_b, _v8_c) = _elem
    _v8_result = (_v8_b, _v8_c)
    if (_v8_result not in R_Q_dS):
        R_Q_dS.add(_v8_result)
        _maint_R_Q_dS_bu_for_R_Q_dS_add(_v8_result)
        _maint_R_Q_T_c_for_R_Q_dS_add(_v8_result)
        _maint_R_Q_T_b_2_for_R_Q_dS_add(_v8_result)
    else:
        R_Q_dS.inccount(_v8_result)

def _maint_R_Q_dS_for_S_remove(_elem):
    (_v9_b, _v9_c) = _elem
    _v9_result = (_v9_b, _v9_c)
    if (R_Q_dS.getcount(_v9_result) == 1):
        _maint_R_Q_T_b_2_for_R_Q_dS_remove(_v9_result)
        _maint_R_Q_T_c_for_R_Q_dS_remove(_v9_result)
        _maint_R_Q_dS_bu_for_R_Q_dS_remove(_v9_result)
        R_Q_dS.remove(_v9_result)
    else:
        R_Q_dS.deccount(_v9_result)

def _maint_R_Q_T_b_1_for_S_add(_elem):
    (_v6_a, _v6_b) = _elem
    _v6_result = (_v6_b,)
    if (_v6_result not in R_Q_T_b_1):
        R_Q_T_b_1.add(_v6_result)
    else:
        R_Q_T_b_1.inccount(_v6_result)

def _maint_R_Q_T_b_1_for_S_remove(_elem):
    (_v7_a, _v7_b) = _elem
    _v7_result = (_v7_b,)
    if (R_Q_T_b_1.getcount(_v7_result) == 1):
        R_Q_T_b_1.remove(_v7_result)
    else:
        R_Q_T_b_1.deccount(_v7_result)

def _maint_R_Q_T_a_for_S_add(_elem):
    (_v4_a, _v4_b) = _elem
    _v4_result = (_v4_a,)
    if (_v4_result not in R_Q_T_a):
        R_Q_T_a.add(_v4_result)
    else:
        R_Q_T_a.inccount(_v4_result)

def _maint_R_Q_T_a_for_S_remove(_elem):
    (_v5_a, _v5_b) = _elem
    _v5_result = (_v5_a,)
    if (R_Q_T_a.getcount(_v5_result) == 1):
        R_Q_T_a.remove(_v5_result)
    else:
        R_Q_T_a.deccount(_v5_result)

def _maint_R_Q_for_S_add(_elem):
    (_v2_a, _v2_b) = _elem
    for (_v2_c,) in R_Q_dS_bu.get((_v2_b,), Set()):
        _v2_result = (_v2_c,)
        if (_v2_result not in R_Q):
            R_Q.add(_v2_result)
        else:
            R_Q.inccount(_v2_result)
    (_v2_b, _v2_c) = _elem
    for (_v2_a,) in S_ub.get((_v2_b,), Set()):
        _v2_result = (_v2_c,)
        if (_v2_result not in R_Q):
            R_Q.add(_v2_result)
        else:
            R_Q.inccount(_v2_result)

def _maint_R_Q_for_S_remove(_elem):
    (_v3_a, _v3_b) = _elem
    for (_v3_c,) in R_Q_dS_bu.get((_v3_b,), Set()):
        _v3_result = (_v3_c,)
        if (R_Q.getcount(_v3_result) == 1):
            R_Q.remove(_v3_result)
        else:
            R_Q.deccount(_v3_result)
    (_v3_b, _v3_c) = _elem
    for (_v3_a,) in S_ub.get((_v3_b,), Set()):
        _v3_result = (_v3_c,)
        if (R_Q.getcount(_v3_result) == 1):
            R_Q.remove(_v3_result)
        else:
            R_Q.deccount(_v3_result)

def main():
    for (x, y) in [(1, 2), (1, 3), (2, 3), (2, 4)]:
        _v1 = (x, y)
        S.add(_v1)
        _maint_S_ub_for_S_add(_v1)
        _maint_R_Q_dS_for_S_add(_v1)
        _maint_R_Q_T_b_1_for_S_add(_v1)
        _maint_R_Q_T_a_for_S_add(_v1)
        _maint_R_Q_for_S_add(_v1)
    print(sorted(R_Q))

if (__name__ == '__main__'):
    main()
