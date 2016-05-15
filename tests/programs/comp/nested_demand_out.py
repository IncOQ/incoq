# Q1 : k -> {(k, a) for (k,) in REL(R__QU_Q1) for (a,) in REL(S) if (a >= k)} : {(Number, Number)}
# Q2 : k, j -> {(k, j, b) for (k, j) in REL(_U_Q2) for (k, b) in REL(R_Q1) if (b <= j)} : {(Number, Number, Number)}
# _QU_Q1 : {(_v2k,) for (_v2k, _v2j) in REL(_U_Q2)} : {(Number)}
from incoq.runtime import *
# S : {(Number)}
S = Set()
# _U_Q2 : {(Number, Number)}
_U_Q2 = Set()
# R__QU_Q1 : {(Number)}
R__QU_Q1 = CSet()
# R_Q1_bu : {Number: {Number}}
R_Q1_bu = Map()
# _U_Q2_bu : {Number: {Number}}
_U_Q2_bu = Map()
# R_Q2_bbu : {(Number, Number): {(Number)}}
R_Q2_bbu = Map()
def _maint_R_Q1_bu_for_R_Q1_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v13_key = _elem_v1
    _v13_value = _elem_v2
    if (_v13_key not in R_Q1_bu):
        _v14 = Set()
        R_Q1_bu[_v13_key] = _v14
    R_Q1_bu[_v13_key].add(_v13_value)

def _maint_R_Q1_bu_for_R_Q1_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v15_key = _elem_v1
    _v15_value = _elem_v2
    R_Q1_bu[_v15_key].remove(_v15_value)
    if (len(R_Q1_bu[_v15_key]) == 0):
        del R_Q1_bu[_v15_key]

def _maint__U_Q2_bu_for__U_Q2_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v16_key = _elem_v1
    _v16_value = _elem_v2
    if (_v16_key not in _U_Q2_bu):
        _v17 = Set()
        _U_Q2_bu[_v16_key] = _v17
    _U_Q2_bu[_v16_key].add(_v16_value)

def _maint_R_Q2_bbu_for_R_Q2_add(_elem):
    (_elem_v1, _elem_v2, _elem_v3) = _elem
    _v19_key = (_elem_v1, _elem_v2)
    _v19_value = (_elem_v3,)
    if (_v19_key not in R_Q2_bbu):
        _v20 = Set()
        R_Q2_bbu[_v19_key] = _v20
    R_Q2_bbu[_v19_key].add(_v19_value)

def _maint_R_Q2_bbu_for_R_Q2_remove(_elem):
    (_elem_v1, _elem_v2, _elem_v3) = _elem
    _v21_key = (_elem_v1, _elem_v2)
    _v21_value = (_elem_v3,)
    R_Q2_bbu[_v21_key].remove(_v21_value)
    if (len(R_Q2_bbu[_v21_key]) == 0):
        del R_Q2_bbu[_v21_key]

def _maint_R_Q2_for__U_Q2_add(_elem):
    (_v9_k, _v9_j) = _elem
    for _v9_b in (R_Q1_bu[_v9_k] if (_v9_k in R_Q1_bu) else ()):
        if (_v9_b <= _v9_j):
            _v9_result = (_v9_k, _v9_j, _v9_b)
            _maint_R_Q2_bbu_for_R_Q2_add(_v9_result)

def _maint_R_Q2_for_R_Q1_add(_elem):
    (_v11_k, _v11_b) = _elem
    for _v11_j in (_U_Q2_bu[_v11_k] if (_v11_k in _U_Q2_bu) else ()):
        if (_v11_b <= _v11_j):
            _v11_result = (_v11_k, _v11_j, _v11_b)
            _maint_R_Q2_bbu_for_R_Q2_add(_v11_result)

def _maint_R_Q2_for_R_Q1_remove(_elem):
    (_v12_k, _v12_b) = _elem
    for _v12_j in (_U_Q2_bu[_v12_k] if (_v12_k in _U_Q2_bu) else ()):
        if (_v12_b <= _v12_j):
            _v12_result = (_v12_k, _v12_j, _v12_b)
            _maint_R_Q2_bbu_for_R_Q2_remove(_v12_result)

def _maint_R_Q1_for_R__QU_Q1_add(_elem):
    (_v5_k,) = _elem
    for (_v5_a,) in S:
        if (_v5_a >= _v5_k):
            _v5_result = (_v5_k, _v5_a)
            _maint_R_Q1_bu_for_R_Q1_add(_v5_result)
            _maint_R_Q2_for_R_Q1_add(_v5_result)

def _maint_R_Q1_for_R__QU_Q1_remove(_elem):
    (_v6_k,) = _elem
    for (_v6_a,) in S:
        if (_v6_a >= _v6_k):
            _v6_result = (_v6_k, _v6_a)
            _maint_R_Q2_for_R_Q1_remove(_v6_result)
            _maint_R_Q1_bu_for_R_Q1_remove(_v6_result)

def _maint_R_Q1_for_S_add(_elem):
    (_v7_a,) = _elem
    for (_v7_k,) in R__QU_Q1:
        if (_v7_a >= _v7_k):
            _v7_result = (_v7_k, _v7_a)
            _maint_R_Q1_bu_for_R_Q1_add(_v7_result)
            _maint_R_Q2_for_R_Q1_add(_v7_result)

def _maint_R__QU_Q1_for__U_Q2_add(_elem):
    (_v3__v2k, _v3__v2j) = _elem
    _v3_result = (_v3__v2k,)
    if (_v3_result not in R__QU_Q1):
        R__QU_Q1.add(_v3_result)
        _maint_R_Q1_for_R__QU_Q1_add(_v3_result)
    else:
        R__QU_Q1.inccount(_v3_result)

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
    print(sorted(((_demand_Q2((k, j)) or True) and (R_Q2_bbu[(k, j)] if ((k, j) in R_Q2_bbu) else Set()))))

if (__name__ == '__main__'):
    main()
