# Q1 : {(a,) for (a, a_2) in REL(S) if (a == a_2)} : {(Number)}
# Q2 : {(w,) for (v,) in REL(R_Q1) for (v, w) in REL(S) for (w,) in REL(T)} : {(Number)}
# Q2_T_v_1 : {(v,) for (v,) in REL(R_Q1)} : Bottom
# Q2_dS : {(v, w) for (v,) in REL(R_Q2_T_v_1) for (v, w) in REL(S)} : Bottom
# Q2_T_w_1 : {(w,) for (v, w) in REL(R_Q2_dS)} : Bottom
# Q2_dT : {(w,) for (w,) in REL(R_Q2_T_w_1) for (w,) in REL(T)} : Bottom
from incoq.mars.runtime import *
# T : {(Number)}
T = Set()
# R_Q1 : {(Number)}
R_Q1 = CSet()
# R_Q2 : {(Number)}
R_Q2 = CSet()
# R_Q2_T_v_1 : Bottom
R_Q2_T_v_1 = Set()
# R_Q2_dS : Bottom
R_Q2_dS = Set()
# R_Q2_T_w_1 : Bottom
R_Q2_T_w_1 = CSet()
# R_Q2_dT : Bottom
R_Q2_dT = Set()
# R_Q2_unwrapped : {Number}
R_Q2_unwrapped = Set()
# S_bu : {Number: {Number}}
S_bu = Map()
# R_Q2_dS_bu : {Bottom: {Bottom}}
R_Q2_dS_bu = Map()
# R_Q2_dS_ub : {Bottom: {Bottom}}
R_Q2_dS_ub = Map()
def _maint_S_bu_for_S_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v23_key = _elem_v1
    _v23_value = _elem_v2
    if (_v23_key not in S_bu):
        _v24 = Set()
        S_bu[_v23_key] = _v24
    S_bu[_v23_key].add(_v23_value)

def _maint_S_bu_for_S_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v25_key = _elem_v1
    _v25_value = _elem_v2
    S_bu[_v25_key].remove(_v25_value)
    if (len(S_bu[_v25_key]) == 0):
        del S_bu[_v25_key]

def _maint_R_Q2_dS_bu_for_R_Q2_dS_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v26_key = _elem_v1
    _v26_value = _elem_v2
    if (_v26_key not in R_Q2_dS_bu):
        _v27 = Set()
        R_Q2_dS_bu[_v26_key] = _v27
    R_Q2_dS_bu[_v26_key].add(_v26_value)

def _maint_R_Q2_dS_bu_for_R_Q2_dS_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v28_key = _elem_v1
    _v28_value = _elem_v2
    R_Q2_dS_bu[_v28_key].remove(_v28_value)
    if (len(R_Q2_dS_bu[_v28_key]) == 0):
        del R_Q2_dS_bu[_v28_key]

def _maint_R_Q2_dS_ub_for_R_Q2_dS_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v29_key = _elem_v2
    _v29_value = _elem_v1
    if (_v29_key not in R_Q2_dS_ub):
        _v30 = Set()
        R_Q2_dS_ub[_v29_key] = _v30
    R_Q2_dS_ub[_v29_key].add(_v29_value)

def _maint_R_Q2_dS_ub_for_R_Q2_dS_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v31_key = _elem_v2
    _v31_value = _elem_v1
    R_Q2_dS_ub[_v31_key].remove(_v31_value)
    if (len(R_Q2_dS_ub[_v31_key]) == 0):
        del R_Q2_dS_ub[_v31_key]

def _maint_R_Q2_unwrapped_for_R_Q2_add(_elem):
    _v32_v = index(_elem, 0)
    R_Q2_unwrapped.add(_v32_v)

def _maint_R_Q2_unwrapped_for_R_Q2_remove(_elem):
    _v33_v = index(_elem, 0)
    R_Q2_unwrapped.remove(_v33_v)

def _maint_R_Q2_dT_for_R_Q2_T_w_1_add(_elem):
    (_v19_w,) = _elem
    if ((_v19_w,) in T):
        _v19_result = (_v19_w,)
        R_Q2_dT.add(_v19_result)

def _maint_R_Q2_dT_for_R_Q2_T_w_1_remove(_elem):
    (_v20_w,) = _elem
    if ((_v20_w,) in T):
        _v20_result = (_v20_w,)
        R_Q2_dT.remove(_v20_result)

def _maint_R_Q2_dT_for_T_add(_elem):
    (_v21_w,) = _elem
    if ((_v21_w,) in R_Q2_T_w_1):
        _v21_result = (_v21_w,)
        R_Q2_dT.add(_v21_result)

def _maint_R_Q2_dT_for_T_remove(_elem):
    (_v22_w,) = _elem
    if ((_v22_w,) in R_Q2_T_w_1):
        _v22_result = (_v22_w,)
        R_Q2_dT.remove(_v22_result)

def _maint_R_Q2_T_w_1_for_R_Q2_dS_add(_elem):
    (_v17_v, _v17_w) = _elem
    _v17_result = (_v17_w,)
    if (_v17_result not in R_Q2_T_w_1):
        R_Q2_T_w_1.add(_v17_result)
        _maint_R_Q2_dT_for_R_Q2_T_w_1_add(_v17_result)
    else:
        R_Q2_T_w_1.inccount(_v17_result)

def _maint_R_Q2_T_w_1_for_R_Q2_dS_remove(_elem):
    (_v18_v, _v18_w) = _elem
    _v18_result = (_v18_w,)
    if (R_Q2_T_w_1.getcount(_v18_result) == 1):
        _maint_R_Q2_dT_for_R_Q2_T_w_1_remove(_v18_result)
        R_Q2_T_w_1.remove(_v18_result)
    else:
        R_Q2_T_w_1.deccount(_v18_result)

def _maint_R_Q2_dS_for_R_Q2_T_v_1_add(_elem):
    (_v13_v,) = _elem
    for _v13_w in (S_bu[_v13_v] if (_v13_v in S_bu) else ()):
        _v13_result = (_v13_v, _v13_w)
        R_Q2_dS.add(_v13_result)
        _maint_R_Q2_dS_bu_for_R_Q2_dS_add(_v13_result)
        _maint_R_Q2_dS_ub_for_R_Q2_dS_add(_v13_result)
        _maint_R_Q2_T_w_1_for_R_Q2_dS_add(_v13_result)

def _maint_R_Q2_dS_for_R_Q2_T_v_1_remove(_elem):
    (_v14_v,) = _elem
    for _v14_w in (S_bu[_v14_v] if (_v14_v in S_bu) else ()):
        _v14_result = (_v14_v, _v14_w)
        _maint_R_Q2_T_w_1_for_R_Q2_dS_remove(_v14_result)
        _maint_R_Q2_dS_ub_for_R_Q2_dS_remove(_v14_result)
        _maint_R_Q2_dS_bu_for_R_Q2_dS_remove(_v14_result)
        R_Q2_dS.remove(_v14_result)

def _maint_R_Q2_dS_for_S_add(_elem):
    (_v15_v, _v15_w) = _elem
    if ((_v15_v,) in R_Q2_T_v_1):
        _v15_result = (_v15_v, _v15_w)
        R_Q2_dS.add(_v15_result)
        _maint_R_Q2_dS_bu_for_R_Q2_dS_add(_v15_result)
        _maint_R_Q2_dS_ub_for_R_Q2_dS_add(_v15_result)
        _maint_R_Q2_T_w_1_for_R_Q2_dS_add(_v15_result)

def _maint_R_Q2_dS_for_S_remove(_elem):
    (_v16_v, _v16_w) = _elem
    if ((_v16_v,) in R_Q2_T_v_1):
        _v16_result = (_v16_v, _v16_w)
        _maint_R_Q2_T_w_1_for_R_Q2_dS_remove(_v16_result)
        _maint_R_Q2_dS_ub_for_R_Q2_dS_remove(_v16_result)
        _maint_R_Q2_dS_bu_for_R_Q2_dS_remove(_v16_result)
        R_Q2_dS.remove(_v16_result)

def _maint_R_Q2_T_v_1_for_R_Q1_add(_elem):
    (_v11_v,) = _elem
    _v11_result = (_v11_v,)
    R_Q2_T_v_1.add(_v11_result)
    _maint_R_Q2_dS_for_R_Q2_T_v_1_add(_v11_result)

def _maint_R_Q2_T_v_1_for_R_Q1_remove(_elem):
    (_v12_v,) = _elem
    _v12_result = (_v12_v,)
    _maint_R_Q2_dS_for_R_Q2_T_v_1_remove(_v12_result)
    R_Q2_T_v_1.remove(_v12_result)

def _maint_R_Q2_for_R_Q1_add(_elem):
    (_v5_v,) = _elem
    if ((_v5_v,) in R_Q1):
        for _v5_w in (R_Q2_dS_bu[_v5_v] if (_v5_v in R_Q2_dS_bu) else ()):
            if ((_v5_w,) in T):
                _v5_result = (_v5_w,)
                if (_v5_result not in R_Q2):
                    R_Q2.add(_v5_result)
                    _maint_R_Q2_unwrapped_for_R_Q2_add(_v5_result)
                else:
                    R_Q2.inccount(_v5_result)

def _maint_R_Q2_for_R_Q1_remove(_elem):
    (_v6_v,) = _elem
    if ((_v6_v,) in R_Q1):
        for _v6_w in (R_Q2_dS_bu[_v6_v] if (_v6_v in R_Q2_dS_bu) else ()):
            if ((_v6_w,) in T):
                _v6_result = (_v6_w,)
                if (R_Q2.getcount(_v6_result) == 1):
                    _maint_R_Q2_unwrapped_for_R_Q2_remove(_v6_result)
                    R_Q2.remove(_v6_result)
                else:
                    R_Q2.deccount(_v6_result)

def _maint_R_Q2_for_S_add(_elem):
    (_v7_v, _v7_w) = _elem
    if ((_v7_v, _v7_w) in R_Q2_dS):
        if ((_v7_v,) in R_Q1):
            if ((_v7_w,) in T):
                _v7_result = (_v7_w,)
                if (_v7_result not in R_Q2):
                    R_Q2.add(_v7_result)
                    _maint_R_Q2_unwrapped_for_R_Q2_add(_v7_result)
                else:
                    R_Q2.inccount(_v7_result)

def _maint_R_Q2_for_S_remove(_elem):
    (_v8_v, _v8_w) = _elem
    if ((_v8_v, _v8_w) in R_Q2_dS):
        if ((_v8_v,) in R_Q1):
            if ((_v8_w,) in T):
                _v8_result = (_v8_w,)
                if (R_Q2.getcount(_v8_result) == 1):
                    _maint_R_Q2_unwrapped_for_R_Q2_remove(_v8_result)
                    R_Q2.remove(_v8_result)
                else:
                    R_Q2.deccount(_v8_result)

def _maint_R_Q2_for_T_add(_elem):
    (_v9_w,) = _elem
    if ((_v9_w,) in R_Q2_dT):
        for _v9_v in (R_Q2_dS_ub[_v9_w] if (_v9_w in R_Q2_dS_ub) else ()):
            if ((_v9_v,) in R_Q1):
                _v9_result = (_v9_w,)
                if (_v9_result not in R_Q2):
                    R_Q2.add(_v9_result)
                    _maint_R_Q2_unwrapped_for_R_Q2_add(_v9_result)
                else:
                    R_Q2.inccount(_v9_result)

def _maint_R_Q2_for_T_remove(_elem):
    (_v10_w,) = _elem
    if ((_v10_w,) in R_Q2_dT):
        for _v10_v in (R_Q2_dS_ub[_v10_w] if (_v10_w in R_Q2_dS_ub) else ()):
            if ((_v10_v,) in R_Q1):
                _v10_result = (_v10_w,)
                if (R_Q2.getcount(_v10_result) == 1):
                    _maint_R_Q2_unwrapped_for_R_Q2_remove(_v10_result)
                    R_Q2.remove(_v10_result)
                else:
                    R_Q2.deccount(_v10_result)

def _maint_R_Q1_for_S_add(_elem):
    (_v3_a, _v3_a_2) = _elem
    if (_v3_a == _v3_a_2):
        _v3_result = (_v3_a,)
        if (_v3_result not in R_Q1):
            R_Q1.add(_v3_result)
            _maint_R_Q2_T_v_1_for_R_Q1_add(_v3_result)
            _maint_R_Q2_for_R_Q1_add(_v3_result)
        else:
            R_Q1.inccount(_v3_result)

def _maint_R_Q1_for_S_remove(_elem):
    (_v4_a, _v4_a_2) = _elem
    if (_v4_a == _v4_a_2):
        _v4_result = (_v4_a,)
        if (R_Q1.getcount(_v4_result) == 1):
            _maint_R_Q2_for_R_Q1_remove(_v4_result)
            _maint_R_Q2_T_v_1_for_R_Q1_remove(_v4_result)
            R_Q1.remove(_v4_result)
        else:
            R_Q1.deccount(_v4_result)

def main():
    for (x, y) in [(1, 1), (1, 2), (2, 2), (2, 3)]:
        _v1 = (x, y)
        _maint_S_bu_for_S_add(_v1)
        _maint_R_Q2_dS_for_S_add(_v1)
        _maint_R_Q2_for_S_add(_v1)
        _maint_R_Q1_for_S_add(_v1)
    _v2 = (3,)
    T.add(_v2)
    _maint_R_Q2_dT_for_T_add(_v2)
    _maint_R_Q2_for_T_add(_v2)
    print(sorted(R_Q2_unwrapped))

if (__name__ == '__main__'):
    main()
