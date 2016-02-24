# Q : z -> {(z, o_f) for (z,) in REL(_U_Q) for (z, o) in M() for (o, o_f) in F(f)} : {({Bottom}, Top)}
# Q_T_z : {(z,) for (z,) in REL(_U_Q)} : Bottom
# Q_d_M : {(z, o) for (z,) in REL(R_Q_T_z) for (z, o) in M()} : Bottom
# Q_T_o : {(o,) for (z, o) in REL(R_Q_d_M)} : Bottom
# Q_d_F_f : {(o, o_f) for (o,) in REL(R_Q_T_o) for (o, o_f) in F(f)} : Bottom
# Q_T_o_f : {(o_f,) for (o, o_f) in REL(R_Q_d_F_f)} : Bottom
from incoq.mars.runtime import *
# _M : {(Top, Top)}
_M = Set()
# _F_f : {(Top, Top)}
_F_f = Set()
# _U_Q : {({Bottom})}
_U_Q = Set()
# R_Q : {({Bottom}, Top)}
R_Q = CSet()
# R_Q_T_z : Bottom
R_Q_T_z = CSet()
# R_Q_d_M : Bottom
R_Q_d_M = CSet()
# R_Q_T_o : Bottom
R_Q_T_o = CSet()
# R_Q_d_F_f : Bottom
R_Q_d_F_f = CSet()
# R_Q_T_o_f : Bottom
R_Q_T_o_f = CSet()
# R_Q_d_M_ub : {(Bottom): {(Bottom)}}
R_Q_d_M_ub = Map()
# R_Q_bu : {({Bottom}): {(Top)}}
R_Q_bu = Map()
def _maint_R_Q_d_M_ub_for_R_Q_d_M_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v23_key = (_elem_v2,)
    _v23_value = (_elem_v1,)
    if (_v23_key not in R_Q_d_M_ub):
        _v24 = Set()
        R_Q_d_M_ub[_v23_key] = _v24
    R_Q_d_M_ub[_v23_key].add(_v23_value)

def _maint_R_Q_d_M_ub_for_R_Q_d_M_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v25_key = (_elem_v2,)
    _v25_value = (_elem_v1,)
    R_Q_d_M_ub[_v25_key].remove(_v25_value)
    if (len(R_Q_d_M_ub[_v25_key]) == 0):
        del R_Q_d_M_ub[_v25_key]

def _maint_R_Q_bu_for_R_Q_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v26_key = (_elem_v1,)
    _v26_value = (_elem_v2,)
    if (_v26_key not in R_Q_bu):
        _v27 = Set()
        R_Q_bu[_v26_key] = _v27
    R_Q_bu[_v26_key].add(_v26_value)

def _maint_R_Q_bu_for_R_Q_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v28_key = (_elem_v1,)
    _v28_value = (_elem_v2,)
    R_Q_bu[_v28_key].remove(_v28_value)
    if (len(R_Q_bu[_v28_key]) == 0):
        del R_Q_bu[_v28_key]

def _maint_R_Q_T_o_f_for_R_Q_d_F_f_add(_elem):
    (_v21_o, _v21_o_f) = _elem
    _v21_result = (_v21_o_f,)
    if (_v21_result not in R_Q_T_o_f):
        R_Q_T_o_f.add(_v21_result)
    else:
        R_Q_T_o_f.inccount(_v21_result)

def _maint_R_Q_T_o_f_for_R_Q_d_F_f_remove(_elem):
    (_v22_o, _v22_o_f) = _elem
    _v22_result = (_v22_o_f,)
    if (R_Q_T_o_f.getcount(_v22_result) == 1):
        R_Q_T_o_f.remove(_v22_result)
    else:
        R_Q_T_o_f.deccount(_v22_result)

def _maint_R_Q_d_F_f_for_R_Q_T_o_add(_elem):
    (_v17_o,) = _elem
    if hasfield(_v17_o, 'f'):
        _v17_o_f = _v17_o.f
        _v17_result = (_v17_o, _v17_o_f)
        if (_v17_result not in R_Q_d_F_f):
            R_Q_d_F_f.add(_v17_result)
            _maint_R_Q_T_o_f_for_R_Q_d_F_f_add(_v17_result)
        else:
            R_Q_d_F_f.inccount(_v17_result)

def _maint_R_Q_d_F_f_for_R_Q_T_o_remove(_elem):
    (_v18_o,) = _elem
    if hasfield(_v18_o, 'f'):
        _v18_o_f = _v18_o.f
        _v18_result = (_v18_o, _v18_o_f)
        if (R_Q_d_F_f.getcount(_v18_result) == 1):
            _maint_R_Q_T_o_f_for_R_Q_d_F_f_remove(_v18_result)
            R_Q_d_F_f.remove(_v18_result)
        else:
            R_Q_d_F_f.deccount(_v18_result)

def _maint_R_Q_d_F_f_for__F_f_add(_elem):
    (_v19_o, _v19_o_f) = _elem
    if ((_v19_o,) in R_Q_T_o):
        _v19_result = (_v19_o, _v19_o_f)
        if (_v19_result not in R_Q_d_F_f):
            R_Q_d_F_f.add(_v19_result)
            _maint_R_Q_T_o_f_for_R_Q_d_F_f_add(_v19_result)
        else:
            R_Q_d_F_f.inccount(_v19_result)

def _maint_R_Q_d_F_f_for__F_f_remove(_elem):
    (_v20_o, _v20_o_f) = _elem
    if ((_v20_o,) in R_Q_T_o):
        _v20_result = (_v20_o, _v20_o_f)
        if (R_Q_d_F_f.getcount(_v20_result) == 1):
            _maint_R_Q_T_o_f_for_R_Q_d_F_f_remove(_v20_result)
            R_Q_d_F_f.remove(_v20_result)
        else:
            R_Q_d_F_f.deccount(_v20_result)

def _maint_R_Q_T_o_for_R_Q_d_M_add(_elem):
    (_v15_z, _v15_o) = _elem
    _v15_result = (_v15_o,)
    if (_v15_result not in R_Q_T_o):
        R_Q_T_o.add(_v15_result)
        _maint_R_Q_d_F_f_for_R_Q_T_o_add(_v15_result)
    else:
        R_Q_T_o.inccount(_v15_result)

def _maint_R_Q_T_o_for_R_Q_d_M_remove(_elem):
    (_v16_z, _v16_o) = _elem
    _v16_result = (_v16_o,)
    if (R_Q_T_o.getcount(_v16_result) == 1):
        _maint_R_Q_d_F_f_for_R_Q_T_o_remove(_v16_result)
        R_Q_T_o.remove(_v16_result)
    else:
        R_Q_T_o.deccount(_v16_result)

def _maint_R_Q_d_M_for_R_Q_T_z_add(_elem):
    (_v11_z,) = _elem
    if isset(_v11_z):
        for _v11_o in _v11_z:
            _v11_result = (_v11_z, _v11_o)
            if (_v11_result not in R_Q_d_M):
                R_Q_d_M.add(_v11_result)
                _maint_R_Q_d_M_ub_for_R_Q_d_M_add(_v11_result)
                _maint_R_Q_T_o_for_R_Q_d_M_add(_v11_result)
            else:
                R_Q_d_M.inccount(_v11_result)

def _maint_R_Q_d_M_for_R_Q_T_z_remove(_elem):
    (_v12_z,) = _elem
    if isset(_v12_z):
        for _v12_o in _v12_z:
            _v12_result = (_v12_z, _v12_o)
            if (R_Q_d_M.getcount(_v12_result) == 1):
                _maint_R_Q_T_o_for_R_Q_d_M_remove(_v12_result)
                _maint_R_Q_d_M_ub_for_R_Q_d_M_remove(_v12_result)
                R_Q_d_M.remove(_v12_result)
            else:
                R_Q_d_M.deccount(_v12_result)

def _maint_R_Q_d_M_for__M_add(_elem):
    (_v13_z, _v13_o) = _elem
    if ((_v13_z,) in R_Q_T_z):
        _v13_result = (_v13_z, _v13_o)
        if (_v13_result not in R_Q_d_M):
            R_Q_d_M.add(_v13_result)
            _maint_R_Q_d_M_ub_for_R_Q_d_M_add(_v13_result)
            _maint_R_Q_T_o_for_R_Q_d_M_add(_v13_result)
        else:
            R_Q_d_M.inccount(_v13_result)

def _maint_R_Q_d_M_for__M_remove(_elem):
    (_v14_z, _v14_o) = _elem
    if ((_v14_z,) in R_Q_T_z):
        _v14_result = (_v14_z, _v14_o)
        if (R_Q_d_M.getcount(_v14_result) == 1):
            _maint_R_Q_T_o_for_R_Q_d_M_remove(_v14_result)
            _maint_R_Q_d_M_ub_for_R_Q_d_M_remove(_v14_result)
            R_Q_d_M.remove(_v14_result)
        else:
            R_Q_d_M.deccount(_v14_result)

def _maint_R_Q_T_z_for__U_Q_add(_elem):
    (_v9_z,) = _elem
    _v9_result = (_v9_z,)
    if (_v9_result not in R_Q_T_z):
        R_Q_T_z.add(_v9_result)
        _maint_R_Q_d_M_for_R_Q_T_z_add(_v9_result)
    else:
        R_Q_T_z.inccount(_v9_result)

def _maint_R_Q_T_z_for__U_Q_remove(_elem):
    (_v10_z,) = _elem
    _v10_result = (_v10_z,)
    if (R_Q_T_z.getcount(_v10_result) == 1):
        _maint_R_Q_d_M_for_R_Q_T_z_remove(_v10_result)
        R_Q_T_z.remove(_v10_result)
    else:
        R_Q_T_z.deccount(_v10_result)

def _maint_R_Q_for__U_Q_add(_elem):
    (_v3_z,) = _elem
    if isset(_v3_z):
        for _v3_o in _v3_z:
            if hasfield(_v3_o, 'f'):
                _v3_o_f = _v3_o.f
                _v3_result = (_v3_z, _v3_o_f)
                if (_v3_result not in R_Q):
                    R_Q.add(_v3_result)
                    _maint_R_Q_bu_for_R_Q_add(_v3_result)
                else:
                    R_Q.inccount(_v3_result)

def _maint_R_Q_for__U_Q_remove(_elem):
    (_v4_z,) = _elem
    if isset(_v4_z):
        for _v4_o in _v4_z:
            if hasfield(_v4_o, 'f'):
                _v4_o_f = _v4_o.f
                _v4_result = (_v4_z, _v4_o_f)
                if (R_Q.getcount(_v4_result) == 1):
                    _maint_R_Q_bu_for_R_Q_remove(_v4_result)
                    R_Q.remove(_v4_result)
                else:
                    R_Q.deccount(_v4_result)

def _maint_R_Q_for__M_add(_elem):
    (_v5_z, _v5_o) = _elem
    if ((_v5_z,) in _U_Q):
        if hasfield(_v5_o, 'f'):
            _v5_o_f = _v5_o.f
            _v5_result = (_v5_z, _v5_o_f)
            if (_v5_result not in R_Q):
                R_Q.add(_v5_result)
                _maint_R_Q_bu_for_R_Q_add(_v5_result)
            else:
                R_Q.inccount(_v5_result)

def _maint_R_Q_for__M_remove(_elem):
    (_v6_z, _v6_o) = _elem
    if ((_v6_z,) in _U_Q):
        if hasfield(_v6_o, 'f'):
            _v6_o_f = _v6_o.f
            _v6_result = (_v6_z, _v6_o_f)
            if (R_Q.getcount(_v6_result) == 1):
                _maint_R_Q_bu_for_R_Q_remove(_v6_result)
                R_Q.remove(_v6_result)
            else:
                R_Q.deccount(_v6_result)

def _maint_R_Q_for__F_f_add(_elem):
    (_v7_o, _v7_o_f) = _elem
    for (_v7_z,) in R_Q_d_M_ub.get((_v7_o,), Set()):
        if ((_v7_z,) in _U_Q):
            _v7_result = (_v7_z, _v7_o_f)
            if (_v7_result not in R_Q):
                R_Q.add(_v7_result)
                _maint_R_Q_bu_for_R_Q_add(_v7_result)
            else:
                R_Q.inccount(_v7_result)

def _maint_R_Q_for__F_f_remove(_elem):
    (_v8_o, _v8_o_f) = _elem
    for (_v8_z,) in R_Q_d_M_ub.get((_v8_o,), Set()):
        if ((_v8_z,) in _U_Q):
            _v8_result = (_v8_z, _v8_o_f)
            if (R_Q.getcount(_v8_result) == 1):
                _maint_R_Q_bu_for_R_Q_remove(_v8_result)
                R_Q.remove(_v8_result)
            else:
                R_Q.deccount(_v8_result)

def _demand_Q(_elem):
    if (_elem not in _U_Q):
        _U_Q.add(_elem)
        _maint_R_Q_T_z_for__U_Q_add(_elem)
        _maint_R_Q_for__U_Q_add(_elem)

def main():
    s = Set()
    t = Set()
    for i in [1, 2, 3, 4]:
        p = Obj()
        _v1 = (p, i)
        index(_v1, 0).f = index(_v1, 1)
        _maint_R_Q_d_F_f_for__F_f_add(_v1)
        _maint_R_Q_for__F_f_add(_v1)
        r = (s if (i % 2) else t)
        _v2 = (r, p)
        index(_v2, 0).add(index(_v2, 1))
        _maint_R_Q_d_M_for__M_add(_v2)
        _maint_R_Q_for__M_add(_v2)
    z = s
    print(sorted(unwrap(((_demand_Q((z,)) or True) and R_Q_bu.get((z,), Set())))))
    z = t
    print(sorted(unwrap(((_demand_Q((z,)) or True) and R_Q_bu.get((z,), Set())))))

if (__name__ == '__main__'):
    main()
