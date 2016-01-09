from incoq.mars.runtime import *
# S : {(Number, Number)}
S = Set()
# _U_Q : {(Number)}
_U_Q = Set()
# R_Q : {(Number, Number)}
R_Q = CSet()
# S_bu : {(Number): {(Number)}}
S_bu = Map()
# R_Q_bu : {(Number): {(Number)}}
R_Q_bu = Map()
def _maint_S_bu_for_S_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v6_key = (_elem_v1,)
    _v6_value = (_elem_v2,)
    if (_v6_key not in S_bu):
        _v7 = Set()
        S_bu[_v6_key] = _v7
    S_bu[_v6_key].add(_v6_value)

def _maint_S_bu_for_S_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v8_key = (_elem_v1,)
    _v8_value = (_elem_v2,)
    S_bu[_v8_key].remove(_v8_value)
    if (len(S_bu[_v8_key]) == 0):
        del S_bu[_v8_key]

def _maint_R_Q_bu_for_R_Q_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v9_key = (_elem_v1,)
    _v9_value = (_elem_v2,)
    if (_v9_key not in R_Q_bu):
        _v10 = Set()
        R_Q_bu[_v9_key] = _v10
    R_Q_bu[_v9_key].add(_v9_value)

def _maint_R_Q_bu_for_R_Q_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v11_key = (_elem_v1,)
    _v11_value = (_elem_v2,)
    R_Q_bu[_v11_key].remove(_v11_value)
    if (len(R_Q_bu[_v11_key]) == 0):
        del R_Q_bu[_v11_key]

def _maint_R_Q_for__U_Q_add(_elem):
    (_v2_a,) = _elem
    for (_v2_b,) in S_bu.get((_v2_a,), Set()):
        _v2_result = (_v2_a, _v2_b)
        if (_v2_result not in R_Q):
            R_Q.add(_v2_result)
            _maint_R_Q_bu_for_R_Q_add(_v2_result)
        else:
            R_Q.inccount(_v2_result)

def _maint_R_Q_for__U_Q_remove(_elem):
    (_v3_a,) = _elem
    for (_v3_b,) in S_bu.get((_v3_a,), Set()):
        _v3_result = (_v3_a, _v3_b)
        if (R_Q.getcount(_v3_result) == 1):
            _maint_R_Q_bu_for_R_Q_remove(_v3_result)
            R_Q.remove(_v3_result)
        else:
            R_Q.deccount(_v3_result)

def _maint_R_Q_for_S_add(_elem):
    (_v4_a, _v4_b) = _elem
    if ((_v4_a,) in _U_Q):
        _v4_result = (_v4_a, _v4_b)
        if (_v4_result not in R_Q):
            R_Q.add(_v4_result)
            _maint_R_Q_bu_for_R_Q_add(_v4_result)
        else:
            R_Q.inccount(_v4_result)

def _maint_R_Q_for_S_remove(_elem):
    (_v5_a, _v5_b) = _elem
    if ((_v5_a,) in _U_Q):
        _v5_result = (_v5_a, _v5_b)
        if (R_Q.getcount(_v5_result) == 1):
            _maint_R_Q_bu_for_R_Q_remove(_v5_result)
            R_Q.remove(_v5_result)
        else:
            R_Q.deccount(_v5_result)

def _demand_Q(_elem):
    if (_elem not in _U_Q):
        _U_Q.add(_elem)
        _maint_R_Q_for__U_Q_add(_elem)

def main():
    for (x, y) in [(1, 2), (2, 3), (3, 4)]:
        _v1 = (x, y)
        S.add(_v1)
        _maint_S_bu_for_S_add(_v1)
        _maint_R_Q_for_S_add(_v1)
    a = 1
    print(((_demand_Q((a,)) or True) and R_Q_bu.get((a,), Set()).unwrap()))

if (__name__ == '__main__'):
    main()
