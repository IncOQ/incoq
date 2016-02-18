# Q : z -> {(o_f,) for (z,) in REL(_U_Q) for (z, o) in M() for (o, o_f) in F(f)} : {({Bottom}, Top)}
from incoq.mars.runtime import *
# _M : {(Top, Top)}
_M = Set()
# _F_f : {(Top, Top)}
_F_f = Set()
# _U_Q : {({Bottom})}
_U_Q = Set()
# R_Q : {({Bottom}, Top)}
R_Q = CSet()
# _M_ub : {(Top): {(Top)}}
_M_ub = Map()
# R_Q_bu : {({Bottom}): {(Top)}}
R_Q_bu = Map()
def _maint__M_ub_for__M_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v9_key = (_elem_v2,)
    _v9_value = (_elem_v1,)
    if (_v9_key not in _M_ub):
        _v10 = Set()
        _M_ub[_v9_key] = _v10
    _M_ub[_v9_key].add(_v9_value)

def _maint__M_ub_for__M_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v11_key = (_elem_v2,)
    _v11_value = (_elem_v1,)
    _M_ub[_v11_key].remove(_v11_value)
    if (len(_M_ub[_v11_key]) == 0):
        del _M_ub[_v11_key]

def _maint_R_Q_bu_for_R_Q_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v12_key = (_elem_v1,)
    _v12_value = (_elem_v2,)
    if (_v12_key not in R_Q_bu):
        _v13 = Set()
        R_Q_bu[_v12_key] = _v13
    R_Q_bu[_v12_key].add(_v12_value)

def _maint_R_Q_bu_for_R_Q_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v14_key = (_elem_v1,)
    _v14_value = (_elem_v2,)
    R_Q_bu[_v14_key].remove(_v14_value)
    if (len(R_Q_bu[_v14_key]) == 0):
        del R_Q_bu[_v14_key]

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
    for (_v7_z,) in _M_ub.get((_v7_o,), Set()):
        if ((_v7_z,) in _U_Q):
            _v7_result = (_v7_z, _v7_o_f)
            if (_v7_result not in R_Q):
                R_Q.add(_v7_result)
                _maint_R_Q_bu_for_R_Q_add(_v7_result)
            else:
                R_Q.inccount(_v7_result)

def _maint_R_Q_for__F_f_remove(_elem):
    (_v8_o, _v8_o_f) = _elem
    for (_v8_z,) in _M_ub.get((_v8_o,), Set()):
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
        _maint_R_Q_for__U_Q_add(_elem)

def main():
    s = Set()
    t = Set()
    for i in [1, 2, 3, 4]:
        p = Obj()
        _v1 = (p, i)
        index(_v1, 0).f = index(_v1, 1)
        _maint_R_Q_for__F_f_add(_v1)
        r = (s if (i % 2) else t)
        _v2 = (r, p)
        index(_v2, 0).add(index(_v2, 1))
        _maint__M_ub_for__M_add(_v2)
        _maint_R_Q_for__M_add(_v2)
    z = s
    print(sorted(unwrap(((_demand_Q((z,)) or True) and R_Q_bu.get((z,), Set())))))
    z = t
    print(sorted(unwrap(((_demand_Q((z,)) or True) and R_Q_bu.get((z,), Set())))))

if (__name__ == '__main__'):
    main()
