# Q1 : x -> {(x, x) for (x,) in REL(S_wrapped)} : {(Number, Number)}
# Q2 : c -> {(c, y) for (c,) in REL(_U_Q2) for (x,) in REL(R_wrapped) if (c == x) for (x, y) in REL(R_Q1)} : {(Number, Number)}
# Q3 : x -> {(x, x2) for (x,) in REL(R__QU_Q3) for (x2,) in REL(S_wrapped) if (x2 != x)} : {(Number, Number)}
# Q4 : x -> max(unwrap(R_Q3.imglookup('bu', (x,))), (x,), R__QU_Q4) : Number
# Q5 : c -> {(c, x) for (c,) in REL(_U_Q5) for (x,) in REL(R_wrapped) if (c == x) for (x, _v28) in SETFROMMAP(SA_Q4, A_Q4, 'bu') if (x != index(_v28, 1))} : {(Number, Number)}
# _QU_Q4 : {(_v5x,) for (_v5c,) in REL(_U_Q5) for (_v5x,) in REL(R_wrapped) if (_v5c == _v5x)} : {(Number)}
# _QU_Q3 : {(_v6x,) for (_v6x,) in REL(R__QU_Q4)} : {(Number)}
from incoq.mars.runtime import *
# R_wrapped : {(Number)}
R_wrapped = Set()
# S_wrapped : {(Number)}
S_wrapped = Set()
# _U_Q2 : {(Number)}
_U_Q2 = Set()
# _U_Q5 : {(Number)}
_U_Q5 = Set()
# R_Q2 : {(Number, Number)}
R_Q2 = CSet()
# R__QU_Q4 : {(Number)}
R__QU_Q4 = CSet()
# R__QU_Q3 : {(Number)}
R__QU_Q3 = Set()
# A_Q4 : {(Number): (Number, Number)}
A_Q4 = Map()
# R_Q3_bu : {Number: {(Number)}}
R_Q3_bu = Map()
# R_Q1_bu : {Number: {Number}}
R_Q1_bu = Map()
# R_Q2_bu : {Number: {Number}}
R_Q2_bu = Map()
# R_Q5_bu : {Number: {Number}}
R_Q5_bu = Map()
def _maint_R_Q3_bu_for_R_Q3_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v37_key = _elem_v1
    _v37_value = (_elem_v2,)
    if (_v37_key not in R_Q3_bu):
        _v38 = Set()
        R_Q3_bu[_v37_key] = _v38
    R_Q3_bu[_v37_key].add(_v37_value)

def _maint_R_Q3_bu_for_R_Q3_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v39_key = _elem_v1
    _v39_value = (_elem_v2,)
    R_Q3_bu[_v39_key].remove(_v39_value)
    if (len(R_Q3_bu[_v39_key]) == 0):
        del R_Q3_bu[_v39_key]

def _maint_R_Q1_bu_for_R_Q1_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v40_key = _elem_v1
    _v40_value = _elem_v2
    if (_v40_key not in R_Q1_bu):
        _v41 = Set()
        R_Q1_bu[_v40_key] = _v41
    R_Q1_bu[_v40_key].add(_v40_value)

def _maint_R_Q1_bu_for_R_Q1_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v42_key = _elem_v1
    _v42_value = _elem_v2
    R_Q1_bu[_v42_key].remove(_v42_value)
    if (len(R_Q1_bu[_v42_key]) == 0):
        del R_Q1_bu[_v42_key]

def _maint_R_Q2_bu_for_R_Q2_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v43_key = _elem_v1
    _v43_value = _elem_v2
    if (_v43_key not in R_Q2_bu):
        _v44 = Set()
        R_Q2_bu[_v43_key] = _v44
    R_Q2_bu[_v43_key].add(_v43_value)

def _maint_R_Q2_bu_for_R_Q2_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v45_key = _elem_v1
    _v45_value = _elem_v2
    R_Q2_bu[_v45_key].remove(_v45_value)
    if (len(R_Q2_bu[_v45_key]) == 0):
        del R_Q2_bu[_v45_key]

def _maint_R_Q5_bu_for_R_Q5_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v46_key = _elem_v1
    _v46_value = _elem_v2
    if (_v46_key not in R_Q5_bu):
        _v47 = Set()
        R_Q5_bu[_v46_key] = _v47
    R_Q5_bu[_v46_key].add(_v46_value)

def _maint_R_Q5_bu_for_R_Q5_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v48_key = _elem_v1
    _v48_value = _elem_v2
    R_Q5_bu[_v48_key].remove(_v48_value)
    if (len(R_Q5_bu[_v48_key]) == 0):
        del R_Q5_bu[_v48_key]

def _maint_R_Q5_for__U_Q5_add(_elem):
    (_v31_c,) = _elem
    for (_v31_x,) in R_wrapped:
        if (_v31_c == _v31_x):
            if ((_v31_x,) in A_Q4):
                _v31__v28 = A_Q4[(_v31_x,)]
                if (_v31_x != index(_v31__v28, 1)):
                    _v31_result = (_v31_c, _v31_x)
                    _maint_R_Q5_bu_for_R_Q5_add(_v31_result)

def _maint_R_Q5_for_R_wrapped_add(_elem):
    (_v33_x,) = _elem
    if ((_v33_x,) in A_Q4):
        _v33__v28 = A_Q4[(_v33_x,)]
        if (_v33_x != index(_v33__v28, 1)):
            for (_v33_c,) in _U_Q5:
                if (_v33_c == _v33_x):
                    _v33_result = (_v33_c, _v33_x)
                    _maint_R_Q5_bu_for_R_Q5_add(_v33_result)

def _maint_R_Q5_for_R_wrapped_remove(_elem):
    (_v34_x,) = _elem
    if ((_v34_x,) in A_Q4):
        _v34__v28 = A_Q4[(_v34_x,)]
        if (_v34_x != index(_v34__v28, 1)):
            for (_v34_c,) in _U_Q5:
                if (_v34_c == _v34_x):
                    _v34_result = (_v34_c, _v34_x)
                    _maint_R_Q5_bu_for_R_Q5_remove(_v34_result)

def _maint_R_Q5_for_SA_Q4_add(_elem):
    (_v35_x, _v35__v28) = _elem
    if ((_v35_x,) in R_wrapped):
        if (_v35_x != index(_v35__v28, 1)):
            for (_v35_c,) in _U_Q5:
                if (_v35_c == _v35_x):
                    _v35_result = (_v35_c, _v35_x)
                    _maint_R_Q5_bu_for_R_Q5_add(_v35_result)

def _maint_R_Q5_for_SA_Q4_remove(_elem):
    (_v36_x, _v36__v28) = _elem
    if ((_v36_x,) in R_wrapped):
        if (_v36_x != index(_v36__v28, 1)):
            for (_v36_c,) in _U_Q5:
                if (_v36_c == _v36_x):
                    _v36_result = (_v36_c, _v36_x)
                    _maint_R_Q5_bu_for_R_Q5_remove(_v36_result)

def _maint_SA_Q4_for_A_Q4_assign(_key, _val):
    (_key_v1,) = _key
    _v29_elem = (_key_v1, _val)
    _maint_R_Q5_for_SA_Q4_add(_v29_elem)

def _maint_SA_Q4_for_A_Q4_delete(_key):
    _val = A_Q4[_key]
    (_key_v1,) = _key
    _v30_elem = (_key_v1, _val)
    _maint_R_Q5_for_SA_Q4_remove(_v30_elem)

def _maint_A_Q4_for_R_Q3_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v25_key = (_elem_v1,)
    _v25_value = _elem_v2
    if (_v25_key in R__QU_Q4):
        _v25_state = A_Q4[_v25_key]
        (_v25tree, _) = _v25_state
        _v25tree[_v25_value] = None
        _v25_state = (_v25tree, _v25tree.__max__())
        _maint_SA_Q4_for_A_Q4_delete(_v25_key)
        del A_Q4[_v25_key]
        A_Q4[_v25_key] = _v25_state
        _maint_SA_Q4_for_A_Q4_assign(_v25_key, _v25_state)

def _maint_A_Q4_for_R_Q3_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v26_key = (_elem_v1,)
    _v26_value = _elem_v2
    if (_v26_key in R__QU_Q4):
        _v26_state = A_Q4[_v26_key]
        (_v26tree, _) = _v26_state
        del _v26tree[_v26_value]
        _v26_state = (_v26tree, _v26tree.__max__())
        _maint_SA_Q4_for_A_Q4_delete(_v26_key)
        del A_Q4[_v26_key]
        A_Q4[_v26_key] = _v26_state
        _maint_SA_Q4_for_A_Q4_assign(_v26_key, _v26_state)

def _maint_A_Q4_for_R__QU_Q4_add(_key):
    _v27_state = (Tree(), None)
    (_key_v1,) = _key
    for (_v27_value,) in (R_Q3_bu[_key_v1] if (_key_v1 in R_Q3_bu) else Set()):
        (_v27tree, _) = _v27_state
        _v27tree[_v27_value] = None
        _v27_state = (_v27tree, _v27tree.__max__())
    A_Q4[_key] = _v27_state
    _maint_SA_Q4_for_A_Q4_assign(_key, _v27_state)

def _maint_A_Q4_for_R__QU_Q4_remove(_key):
    _maint_SA_Q4_for_A_Q4_delete(_key)
    del A_Q4[_key]

def _maint_R_Q3_for_R__QU_Q3_add(_elem):
    (_v21_x,) = _elem
    for (_v21_x2,) in S_wrapped:
        if (_v21_x2 != _v21_x):
            _v21_result = (_v21_x, _v21_x2)
            _maint_R_Q3_bu_for_R_Q3_add(_v21_result)
            _maint_A_Q4_for_R_Q3_add(_v21_result)

def _maint_R_Q3_for_R__QU_Q3_remove(_elem):
    (_v22_x,) = _elem
    for (_v22_x2,) in S_wrapped:
        if (_v22_x2 != _v22_x):
            _v22_result = (_v22_x, _v22_x2)
            _maint_A_Q4_for_R_Q3_remove(_v22_result)
            _maint_R_Q3_bu_for_R_Q3_remove(_v22_result)

def _maint_R_Q3_for_S_wrapped_add(_elem):
    (_v23_x2,) = _elem
    for (_v23_x,) in R__QU_Q3:
        if (_v23_x2 != _v23_x):
            _v23_result = (_v23_x, _v23_x2)
            _maint_R_Q3_bu_for_R_Q3_add(_v23_result)
            _maint_A_Q4_for_R_Q3_add(_v23_result)

def _maint_R_Q3_for_S_wrapped_remove(_elem):
    (_v24_x2,) = _elem
    for (_v24_x,) in R__QU_Q3:
        if (_v24_x2 != _v24_x):
            _v24_result = (_v24_x, _v24_x2)
            _maint_A_Q4_for_R_Q3_remove(_v24_result)
            _maint_R_Q3_bu_for_R_Q3_remove(_v24_result)

def _maint_R__QU_Q3_for_R__QU_Q4_add(_elem):
    (_v19__v6x,) = _elem
    _v19_result = (_v19__v6x,)
    R__QU_Q3.add(_v19_result)
    _maint_R_Q3_for_R__QU_Q3_add(_v19_result)

def _maint_R__QU_Q3_for_R__QU_Q4_remove(_elem):
    (_v20__v6x,) = _elem
    _v20_result = (_v20__v6x,)
    _maint_R_Q3_for_R__QU_Q3_remove(_v20_result)
    R__QU_Q3.remove(_v20_result)

def _maint_R__QU_Q4_for__U_Q5_add(_elem):
    (_v15__v5c,) = _elem
    for (_v15__v5x,) in R_wrapped:
        if (_v15__v5c == _v15__v5x):
            _v15_result = (_v15__v5x,)
            if (_v15_result not in R__QU_Q4):
                R__QU_Q4.add(_v15_result)
                _maint_A_Q4_for_R__QU_Q4_add(_v15_result)
                _maint_R__QU_Q3_for_R__QU_Q4_add(_v15_result)
            else:
                R__QU_Q4.inccount(_v15_result)

def _maint_R__QU_Q4_for_R_wrapped_add(_elem):
    (_v17__v5x,) = _elem
    for (_v17__v5c,) in _U_Q5:
        if (_v17__v5c == _v17__v5x):
            _v17_result = (_v17__v5x,)
            if (_v17_result not in R__QU_Q4):
                R__QU_Q4.add(_v17_result)
                _maint_A_Q4_for_R__QU_Q4_add(_v17_result)
                _maint_R__QU_Q3_for_R__QU_Q4_add(_v17_result)
            else:
                R__QU_Q4.inccount(_v17_result)

def _maint_R__QU_Q4_for_R_wrapped_remove(_elem):
    (_v18__v5x,) = _elem
    for (_v18__v5c,) in _U_Q5:
        if (_v18__v5c == _v18__v5x):
            _v18_result = (_v18__v5x,)
            if (R__QU_Q4.getcount(_v18_result) == 1):
                _maint_R__QU_Q3_for_R__QU_Q4_remove(_v18_result)
                _maint_A_Q4_for_R__QU_Q4_remove(_v18_result)
                R__QU_Q4.remove(_v18_result)
            else:
                R__QU_Q4.deccount(_v18_result)

def _maint_R_Q2_for__U_Q2_add(_elem):
    (_v9_c,) = _elem
    for (_v9_x,) in R_wrapped:
        if (_v9_c == _v9_x):
            for _v9_y in (R_Q1_bu[_v9_x] if (_v9_x in R_Q1_bu) else ()):
                _v9_result = (_v9_c, _v9_y)
                if (_v9_result not in R_Q2):
                    R_Q2.add(_v9_result)
                    _maint_R_Q2_bu_for_R_Q2_add(_v9_result)
                else:
                    R_Q2.inccount(_v9_result)

def _maint_R_Q2_for_R_wrapped_add(_elem):
    (_v11_x,) = _elem
    for _v11_y in (R_Q1_bu[_v11_x] if (_v11_x in R_Q1_bu) else ()):
        for (_v11_c,) in _U_Q2:
            if (_v11_c == _v11_x):
                _v11_result = (_v11_c, _v11_y)
                if (_v11_result not in R_Q2):
                    R_Q2.add(_v11_result)
                    _maint_R_Q2_bu_for_R_Q2_add(_v11_result)
                else:
                    R_Q2.inccount(_v11_result)

def _maint_R_Q2_for_R_wrapped_remove(_elem):
    (_v12_x,) = _elem
    for _v12_y in (R_Q1_bu[_v12_x] if (_v12_x in R_Q1_bu) else ()):
        for (_v12_c,) in _U_Q2:
            if (_v12_c == _v12_x):
                _v12_result = (_v12_c, _v12_y)
                if (R_Q2.getcount(_v12_result) == 1):
                    _maint_R_Q2_bu_for_R_Q2_remove(_v12_result)
                    R_Q2.remove(_v12_result)
                else:
                    R_Q2.deccount(_v12_result)

def _maint_R_Q2_for_R_Q1_add(_elem):
    (_v13_x, _v13_y) = _elem
    if ((_v13_x,) in R_wrapped):
        for (_v13_c,) in _U_Q2:
            if (_v13_c == _v13_x):
                _v13_result = (_v13_c, _v13_y)
                if (_v13_result not in R_Q2):
                    R_Q2.add(_v13_result)
                    _maint_R_Q2_bu_for_R_Q2_add(_v13_result)
                else:
                    R_Q2.inccount(_v13_result)

def _maint_R_Q2_for_R_Q1_remove(_elem):
    (_v14_x, _v14_y) = _elem
    if ((_v14_x,) in R_wrapped):
        for (_v14_c,) in _U_Q2:
            if (_v14_c == _v14_x):
                _v14_result = (_v14_c, _v14_y)
                if (R_Q2.getcount(_v14_result) == 1):
                    _maint_R_Q2_bu_for_R_Q2_remove(_v14_result)
                    R_Q2.remove(_v14_result)
                else:
                    R_Q2.deccount(_v14_result)

def _maint_R_Q1_for_S_wrapped_add(_elem):
    (_v7_x,) = _elem
    _v7_result = (_v7_x, _v7_x)
    _maint_R_Q1_bu_for_R_Q1_add(_v7_result)
    _maint_R_Q2_for_R_Q1_add(_v7_result)

def _maint_R_Q1_for_S_wrapped_remove(_elem):
    (_v8_x,) = _elem
    _v8_result = (_v8_x, _v8_x)
    _maint_R_Q2_for_R_Q1_remove(_v8_result)
    _maint_R_Q1_bu_for_R_Q1_remove(_v8_result)

def _demand_Q2(_elem):
    if (_elem not in _U_Q2):
        _U_Q2.add(_elem)
        _maint_R_Q2_for__U_Q2_add(_elem)

def _demand_Q5(_elem):
    if (_elem not in _U_Q5):
        _U_Q5.add(_elem)
        _maint_R_Q5_for__U_Q5_add(_elem)
        _maint_R__QU_Q4_for__U_Q5_add(_elem)

def _maint_R_wrapped_for_R_add(_elem):
    _v1_v = (_elem,)
    R_wrapped.add(_v1_v)
    _maint_R_Q5_for_R_wrapped_add(_v1_v)
    _maint_R__QU_Q4_for_R_wrapped_add(_v1_v)
    _maint_R_Q2_for_R_wrapped_add(_v1_v)

def _maint_S_wrapped_for_S_add(_elem):
    _v3_v = (_elem,)
    S_wrapped.add(_v3_v)
    _maint_R_Q3_for_S_wrapped_add(_v3_v)
    _maint_R_Q1_for_S_wrapped_add(_v3_v)

def main():
    for v in [1, 2, 3]:
        _maint_R_wrapped_for_R_add(v)
        _maint_S_wrapped_for_S_add(v)
    c = 2
    print(sorted(((_demand_Q2((c,)) or True) and (R_Q2_bu[c] if (c in R_Q2_bu) else Set()))))
    print(sorted(((_demand_Q5((c,)) or True) and (R_Q5_bu[c] if (c in R_Q5_bu) else Set()))))

if (__name__ == '__main__'):
    main()
