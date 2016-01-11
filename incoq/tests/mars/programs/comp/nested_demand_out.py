from incoq.mars.runtime import *
# S : {(Number)}
S = Set()
# _U_Q2 : {(Number, Number)}
_U_Q2 = Set()
# R__QU_Q1 : {(Number, Number, Number)}
R__QU_Q1 = CSet()
# R_Q1 : {(Number, Number)}
R_Q1 = CSet()
# R_Q2 : {(Number, Number, Number)}
R_Q2 = CSet()
# R_Q1_bu : {(Number): {(Number)}}
R_Q1_bu = Map()
# _U_Q2_bu : {(Number): {(Number)}}
_U_Q2_bu = Map()
# R_Q2_bbu : {(Number, Number): {(Number)}}
R_Q2_bbu = Map()
def _maint_R_Q1_bu_for_R_Q1_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v12_key = (_elem_v1,)
    _v12_value = (_elem_v2,)
    if (_v12_key not in R_Q1_bu):
        _v13 = Set()
        R_Q1_bu[_v12_key] = _v13
    R_Q1_bu[_v12_key].add(_v12_value)

def _maint_R_Q1_bu_for_R_Q1_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v14_key = (_elem_v1,)
    _v14_value = (_elem_v2,)
    R_Q1_bu[_v14_key].remove(_v14_value)
    if (len(R_Q1_bu[_v14_key]) == 0):
        del R_Q1_bu[_v14_key]

def _maint__U_Q2_bu_for__U_Q2_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v15_key = (_elem_v1,)
    _v15_value = (_elem_v2,)
    if (_v15_key not in _U_Q2_bu):
        _v16 = Set()
        _U_Q2_bu[_v15_key] = _v16
    _U_Q2_bu[_v15_key].add(_v15_value)

def _maint__U_Q2_bu_for__U_Q2_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v17_key = (_elem_v1,)
    _v17_value = (_elem_v2,)
    _U_Q2_bu[_v17_key].remove(_v17_value)
    if (len(_U_Q2_bu[_v17_key]) == 0):
        del _U_Q2_bu[_v17_key]

def _maint_R_Q2_bbu_for_R_Q2_add(_elem):
    (_elem_v1, _elem_v2, _elem_v3) = _elem
    _v18_key = (_elem_v1, _elem_v2)
    _v18_value = (_elem_v3,)
    if (_v18_key not in R_Q2_bbu):
        _v19 = Set()
        R_Q2_bbu[_v18_key] = _v19
    R_Q2_bbu[_v18_key].add(_v18_value)

def _maint_R_Q2_bbu_for_R_Q2_remove(_elem):
    (_elem_v1, _elem_v2, _elem_v3) = _elem
    _v20_key = (_elem_v1, _elem_v2)
    _v20_value = (_elem_v3,)
    R_Q2_bbu[_v20_key].remove(_v20_value)
    if (len(R_Q2_bbu[_v20_key]) == 0):
        del R_Q2_bbu[_v20_key]

def _maint_R_Q2_for__U_Q2_add(_elem):
    (_v8_k, _v8_j) = _elem
    for (_v8_b,) in R_Q1_bu.get((_v8_k,), Set()):
        if (_v8_b <= _v8_j):
            _v8_result = (_v8_k, _v8_j, _v8_b)
            if (_v8_result not in R_Q2):
                R_Q2.add(_v8_result)
                _maint_R_Q2_bbu_for_R_Q2_add(_v8_result)
            else:
                R_Q2.inccount(_v8_result)

def _maint_R_Q2_for__U_Q2_remove(_elem):
    (_v9_k, _v9_j) = _elem
    for (_v9_b,) in R_Q1_bu.get((_v9_k,), Set()):
        if (_v9_b <= _v9_j):
            _v9_result = (_v9_k, _v9_j, _v9_b)
            if (R_Q2.getcount(_v9_result) == 1):
                _maint_R_Q2_bbu_for_R_Q2_remove(_v9_result)
                R_Q2.remove(_v9_result)
            else:
                R_Q2.deccount(_v9_result)

def _maint_R_Q2_for_R_Q1_add(_elem):
    (_v10_k, _v10_b) = _elem
    for (_v10_j,) in _U_Q2_bu.get((_v10_k,), Set()):
        if (_v10_b <= _v10_j):
            _v10_result = (_v10_k, _v10_j, _v10_b)
            if (_v10_result not in R_Q2):
                R_Q2.add(_v10_result)
                _maint_R_Q2_bbu_for_R_Q2_add(_v10_result)
            else:
                R_Q2.inccount(_v10_result)

def _maint_R_Q2_for_R_Q1_remove(_elem):
    (_v11_k, _v11_b) = _elem
    for (_v11_j,) in _U_Q2_bu.get((_v11_k,), Set()):
        if (_v11_b <= _v11_j):
            _v11_result = (_v11_k, _v11_j, _v11_b)
            if (R_Q2.getcount(_v11_result) == 1):
                _maint_R_Q2_bbu_for_R_Q2_remove(_v11_result)
                R_Q2.remove(_v11_result)
            else:
                R_Q2.deccount(_v11_result)

def _maint_R_Q1_for_R__QU_Q1_add(_elem):
    (_v4_k, _v4_j, _v4_k_2) = _elem
    if (_v4_k == _v4_k_2):
        for (_v4_a,) in S:
            if (_v4_a >= _v4_k):
                _v4_result = (_v4_k, _v4_a)
                if (_v4_result not in R_Q1):
                    R_Q1.add(_v4_result)
                    _maint_R_Q1_bu_for_R_Q1_add(_v4_result)
                    _maint_R_Q2_for_R_Q1_add(_v4_result)
                else:
                    R_Q1.inccount(_v4_result)

def _maint_R_Q1_for_R__QU_Q1_remove(_elem):
    (_v5_k, _v5_j, _v5_k_2) = _elem
    if (_v5_k == _v5_k_2):
        for (_v5_a,) in S:
            if (_v5_a >= _v5_k):
                _v5_result = (_v5_k, _v5_a)
                if (R_Q1.getcount(_v5_result) == 1):
                    _maint_R_Q2_for_R_Q1_remove(_v5_result)
                    _maint_R_Q1_bu_for_R_Q1_remove(_v5_result)
                    R_Q1.remove(_v5_result)
                else:
                    R_Q1.deccount(_v5_result)

def _maint_R_Q1_for_S_add(_elem):
    (_v6_a,) = _elem
    for (_v6_k, _v6_j, _v6_k_2) in R__QU_Q1:
        if (_v6_k == _v6_k_2):
            if (_v6_a >= _v6_k):
                _v6_result = (_v6_k, _v6_a)
                if (_v6_result not in R_Q1):
                    R_Q1.add(_v6_result)
                    _maint_R_Q1_bu_for_R_Q1_add(_v6_result)
                    _maint_R_Q2_for_R_Q1_add(_v6_result)
                else:
                    R_Q1.inccount(_v6_result)

def _maint_R_Q1_for_S_remove(_elem):
    (_v7_a,) = _elem
    for (_v7_k, _v7_j, _v7_k_2) in R__QU_Q1:
        if (_v7_k == _v7_k_2):
            if (_v7_a >= _v7_k):
                _v7_result = (_v7_k, _v7_a)
                if (R_Q1.getcount(_v7_result) == 1):
                    _maint_R_Q2_for_R_Q1_remove(_v7_result)
                    _maint_R_Q1_bu_for_R_Q1_remove(_v7_result)
                    R_Q1.remove(_v7_result)
                else:
                    R_Q1.deccount(_v7_result)

def _maint_R__QU_Q1_for__U_Q2_add(_elem):
    (_v2_k, _v2_j) = _elem
    _v2_result = (_v2_k, _v2_j, _v2_k)
    if (_v2_result not in R__QU_Q1):
        R__QU_Q1.add(_v2_result)
        _maint_R_Q1_for_R__QU_Q1_add(_v2_result)
    else:
        R__QU_Q1.inccount(_v2_result)

def _maint_R__QU_Q1_for__U_Q2_remove(_elem):
    (_v3_k, _v3_j) = _elem
    _v3_result = (_v3_k, _v3_j, _v3_k)
    if (R__QU_Q1.getcount(_v3_result) == 1):
        _maint_R_Q1_for_R__QU_Q1_remove(_v3_result)
        R__QU_Q1.remove(_v3_result)
    else:
        R__QU_Q1.deccount(_v3_result)

def _demand_Q2(_elem):
    if (_elem not in _U_Q2):
        _U_Q2.add(_elem)
        _maint__U_Q2_bu_for__U_Q2_add(_elem)
        _maint_R_Q2_for__U_Q2_add(_elem)
        _maint_R__QU_Q1_for__U_Q2_add(_elem)

def main():
    for x in [1, 2, 3, 4, 5]:
        _v1 = (x,)
        S.add(_v1)
        _maint_R_Q1_for_S_add(_v1)
    k = 2
    j = 4
    print(((_demand_Q2((k, j)) or True) and R_Q2_bbu.get((k, j), Set()).unwrap()))

if (__name__ == '__main__'):
    main()
