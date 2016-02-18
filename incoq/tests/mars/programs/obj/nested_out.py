# Q2 : z -> {(m,) for (z,) in VARS(R__QU_Q2) for (z, m) in M()} : {({Bottom}, Bottom)}
# Q1 : z -> {(o_f,) for (z,) in REL(_U_Q1) for (o,) in VARS(R_Q2.imglookup('bu', (z,))) for (o, o_f) in F(f)} : {({Bottom}, Top)}
# _QU_Q2 : {(_v3z,) for (_v3z,) in REL(_U_Q1)} : {({Bottom})}
from incoq.mars.runtime import *
# _M : {(Top, Top)}
_M = Set()
# _F_f : {(Top, Top)}
_F_f = Set()
# _U_Q1 : {({Bottom})}
_U_Q1 = Set()
# R__QU_Q2 : {({Bottom})}
R__QU_Q2 = CSet()
# R_Q2 : {({Bottom}, Bottom)}
R_Q2 = CSet()
# R_Q1 : {({Bottom}, Top)}
R_Q1 = CSet()
# R_Q2_bu : {({Bottom}): {(Bottom)}}
R_Q2_bu = Map()
# R_Q2_ub : {(Bottom): {({Bottom})}}
R_Q2_ub = Map()
# R_Q1_bu : {({Bottom}): {(Top)}}
R_Q1_bu = Map()
def _maint_R_Q2_bu_for_R_Q2_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v16_key = (_elem_v1,)
    _v16_value = (_elem_v2,)
    if (_v16_key not in R_Q2_bu):
        _v17 = Set()
        R_Q2_bu[_v16_key] = _v17
    R_Q2_bu[_v16_key].add(_v16_value)

def _maint_R_Q2_bu_for_R_Q2_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v18_key = (_elem_v1,)
    _v18_value = (_elem_v2,)
    R_Q2_bu[_v18_key].remove(_v18_value)
    if (len(R_Q2_bu[_v18_key]) == 0):
        del R_Q2_bu[_v18_key]

def _maint_R_Q2_ub_for_R_Q2_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v19_key = (_elem_v2,)
    _v19_value = (_elem_v1,)
    if (_v19_key not in R_Q2_ub):
        _v20 = Set()
        R_Q2_ub[_v19_key] = _v20
    R_Q2_ub[_v19_key].add(_v19_value)

def _maint_R_Q2_ub_for_R_Q2_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v21_key = (_elem_v2,)
    _v21_value = (_elem_v1,)
    R_Q2_ub[_v21_key].remove(_v21_value)
    if (len(R_Q2_ub[_v21_key]) == 0):
        del R_Q2_ub[_v21_key]

def _maint_R_Q1_bu_for_R_Q1_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v22_key = (_elem_v1,)
    _v22_value = (_elem_v2,)
    if (_v22_key not in R_Q1_bu):
        _v23 = Set()
        R_Q1_bu[_v22_key] = _v23
    R_Q1_bu[_v22_key].add(_v22_value)

def _maint_R_Q1_bu_for_R_Q1_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v24_key = (_elem_v1,)
    _v24_value = (_elem_v2,)
    R_Q1_bu[_v24_key].remove(_v24_value)
    if (len(R_Q1_bu[_v24_key]) == 0):
        del R_Q1_bu[_v24_key]

def _maint_R_Q1_for__U_Q1_add(_elem):
    (_v10_z,) = _elem
    for (_v10_o,) in R_Q2_bu.get((_v10_z,), Set()):
        if hasfield(_v10_o, 'f'):
            _v10_o_f = _v10_o.f
            _v10_result = (_v10_z, _v10_o_f)
            if (_v10_result not in R_Q1):
                R_Q1.add(_v10_result)
                _maint_R_Q1_bu_for_R_Q1_add(_v10_result)
            else:
                R_Q1.inccount(_v10_result)

def _maint_R_Q1_for__U_Q1_remove(_elem):
    (_v11_z,) = _elem
    for (_v11_o,) in R_Q2_bu.get((_v11_z,), Set()):
        if hasfield(_v11_o, 'f'):
            _v11_o_f = _v11_o.f
            _v11_result = (_v11_z, _v11_o_f)
            if (R_Q1.getcount(_v11_result) == 1):
                _maint_R_Q1_bu_for_R_Q1_remove(_v11_result)
                R_Q1.remove(_v11_result)
            else:
                R_Q1.deccount(_v11_result)

def _maint_R_Q1_for_R_Q2_add(_elem):
    (_v12_z, _v12_o) = _elem
    if ((_v12_z,) in _U_Q1):
        if hasfield(_v12_o, 'f'):
            _v12_o_f = _v12_o.f
            _v12_result = (_v12_z, _v12_o_f)
            if (_v12_result not in R_Q1):
                R_Q1.add(_v12_result)
                _maint_R_Q1_bu_for_R_Q1_add(_v12_result)
            else:
                R_Q1.inccount(_v12_result)

def _maint_R_Q1_for_R_Q2_remove(_elem):
    (_v13_z, _v13_o) = _elem
    if ((_v13_z,) in _U_Q1):
        if hasfield(_v13_o, 'f'):
            _v13_o_f = _v13_o.f
            _v13_result = (_v13_z, _v13_o_f)
            if (R_Q1.getcount(_v13_result) == 1):
                _maint_R_Q1_bu_for_R_Q1_remove(_v13_result)
                R_Q1.remove(_v13_result)
            else:
                R_Q1.deccount(_v13_result)

def _maint_R_Q1_for__F_f_add(_elem):
    (_v14_o, _v14_o_f) = _elem
    for (_v14_z,) in R_Q2_ub.get((_v14_o,), Set()):
        if ((_v14_z,) in _U_Q1):
            _v14_result = (_v14_z, _v14_o_f)
            if (_v14_result not in R_Q1):
                R_Q1.add(_v14_result)
                _maint_R_Q1_bu_for_R_Q1_add(_v14_result)
            else:
                R_Q1.inccount(_v14_result)

def _maint_R_Q1_for__F_f_remove(_elem):
    (_v15_o, _v15_o_f) = _elem
    for (_v15_z,) in R_Q2_ub.get((_v15_o,), Set()):
        if ((_v15_z,) in _U_Q1):
            _v15_result = (_v15_z, _v15_o_f)
            if (R_Q1.getcount(_v15_result) == 1):
                _maint_R_Q1_bu_for_R_Q1_remove(_v15_result)
                R_Q1.remove(_v15_result)
            else:
                R_Q1.deccount(_v15_result)

def _maint_R_Q2_for_R__QU_Q2_add(_elem):
    (_v6_z,) = _elem
    if isset(_v6_z):
        for _v6_m in _v6_z:
            _v6_result = (_v6_z, _v6_m)
            if (_v6_result not in R_Q2):
                R_Q2.add(_v6_result)
                _maint_R_Q2_bu_for_R_Q2_add(_v6_result)
                _maint_R_Q2_ub_for_R_Q2_add(_v6_result)
                _maint_R_Q1_for_R_Q2_add(_v6_result)
            else:
                R_Q2.inccount(_v6_result)

def _maint_R_Q2_for_R__QU_Q2_remove(_elem):
    (_v7_z,) = _elem
    if isset(_v7_z):
        for _v7_m in _v7_z:
            _v7_result = (_v7_z, _v7_m)
            if (R_Q2.getcount(_v7_result) == 1):
                _maint_R_Q1_for_R_Q2_remove(_v7_result)
                _maint_R_Q2_ub_for_R_Q2_remove(_v7_result)
                _maint_R_Q2_bu_for_R_Q2_remove(_v7_result)
                R_Q2.remove(_v7_result)
            else:
                R_Q2.deccount(_v7_result)

def _maint_R_Q2_for__M_add(_elem):
    (_v8_z, _v8_m) = _elem
    if ((_v8_z,) in R__QU_Q2):
        _v8_result = (_v8_z, _v8_m)
        if (_v8_result not in R_Q2):
            R_Q2.add(_v8_result)
            _maint_R_Q2_bu_for_R_Q2_add(_v8_result)
            _maint_R_Q2_ub_for_R_Q2_add(_v8_result)
            _maint_R_Q1_for_R_Q2_add(_v8_result)
        else:
            R_Q2.inccount(_v8_result)

def _maint_R_Q2_for__M_remove(_elem):
    (_v9_z, _v9_m) = _elem
    if ((_v9_z,) in R__QU_Q2):
        _v9_result = (_v9_z, _v9_m)
        if (R_Q2.getcount(_v9_result) == 1):
            _maint_R_Q1_for_R_Q2_remove(_v9_result)
            _maint_R_Q2_ub_for_R_Q2_remove(_v9_result)
            _maint_R_Q2_bu_for_R_Q2_remove(_v9_result)
            R_Q2.remove(_v9_result)
        else:
            R_Q2.deccount(_v9_result)

def _maint_R__QU_Q2_for__U_Q1_add(_elem):
    (_v4__v3z,) = _elem
    _v4_result = (_v4__v3z,)
    if (_v4_result not in R__QU_Q2):
        R__QU_Q2.add(_v4_result)
        _maint_R_Q2_for_R__QU_Q2_add(_v4_result)
    else:
        R__QU_Q2.inccount(_v4_result)

def _maint_R__QU_Q2_for__U_Q1_remove(_elem):
    (_v5__v3z,) = _elem
    _v5_result = (_v5__v3z,)
    if (R__QU_Q2.getcount(_v5_result) == 1):
        _maint_R_Q2_for_R__QU_Q2_remove(_v5_result)
        R__QU_Q2.remove(_v5_result)
    else:
        R__QU_Q2.deccount(_v5_result)

def _demand_Q1(_elem):
    if (_elem not in _U_Q1):
        _U_Q1.add(_elem)
        _maint_R_Q1_for__U_Q1_add(_elem)
        _maint_R__QU_Q2_for__U_Q1_add(_elem)

def main():
    s = Set()
    t = Set()
    for i in [1, 2, 3, 4]:
        p = Obj()
        _v1 = (p, i)
        index(_v1, 0).f = index(_v1, 1)
        _maint_R_Q1_for__F_f_add(_v1)
        r = (s if (i % 2) else t)
        _v2 = (r, p)
        index(_v2, 0).add(index(_v2, 1))
        _maint_R_Q2_for__M_add(_v2)
    z = s
    print(sorted(unwrap(((_demand_Q1((z,)) or True) and R_Q1_bu.get((z,), Set())))))
    z = t
    print(sorted(unwrap(((_demand_Q1((z,)) or True) and R_Q1_bu.get((z,), Set())))))

if (__name__ == '__main__'):
    main()
