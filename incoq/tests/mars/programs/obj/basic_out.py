# Q1 : z -> {(z, o_f) for (z,) in REL(_U_Q1) for (z, o) in M() for (o, o_f) in F(f)} : {({Top}, Top)}
# Q2 : s, t -> {(s, t, o_f) for (s, t) in REL(_U_Q2) for (s, o) in M() for (t, o) in M() for (o, o_f) in F(f)} : {({Top}, {Top}, Top)}
from incoq.mars.runtime import *
# _U_Q1 : {({Top})}
_U_Q1 = Set()
# _U_Q2 : {({Top}, {Top})}
_U_Q2 = Set()
# R_Q1 : {({Top}, Top)}
R_Q1 = CSet()
# R_Q2 : {({Top}, {Top}, Top)}
R_Q2 = CSet()
# _U_Q2_bu : {{Top}: {{Top}}}
_U_Q2_bu = Map()
# _U_Q2_ub : {{Top}: {{Top}}}
_U_Q2_ub = Map()
# _M_ub : {Top: {Top}}
_M_ub = Map()
# R_Q1_bu : {{Top}: {Top}}
R_Q1_bu = Map()
# R_Q2_bbu : {({Top}, {Top}): {Top}}
R_Q2_bbu = Map()
def _maint__U_Q2_bu_for__U_Q2_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v20_key = _elem_v1
    _v20_value = _elem_v2
    if (_v20_key not in _U_Q2_bu):
        _v21 = Set()
        _U_Q2_bu[_v20_key] = _v21
    _U_Q2_bu[_v20_key].add(_v20_value)

def _maint__U_Q2_bu_for__U_Q2_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v22_key = _elem_v1
    _v22_value = _elem_v2
    _U_Q2_bu[_v22_key].remove(_v22_value)
    if (len(_U_Q2_bu[_v22_key]) == 0):
        del _U_Q2_bu[_v22_key]

def _maint__U_Q2_ub_for__U_Q2_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v23_key = _elem_v2
    _v23_value = _elem_v1
    if (_v23_key not in _U_Q2_ub):
        _v24 = Set()
        _U_Q2_ub[_v23_key] = _v24
    _U_Q2_ub[_v23_key].add(_v23_value)

def _maint__U_Q2_ub_for__U_Q2_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v25_key = _elem_v2
    _v25_value = _elem_v1
    _U_Q2_ub[_v25_key].remove(_v25_value)
    if (len(_U_Q2_ub[_v25_key]) == 0):
        del _U_Q2_ub[_v25_key]

def _maint__M_ub_for__M_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v26_key = _elem_v2
    _v26_value = _elem_v1
    if (_v26_key not in _M_ub):
        _v27 = Set()
        _M_ub[_v26_key] = _v27
    _M_ub[_v26_key].add(_v26_value)

def _maint__M_ub_for__M_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v28_key = _elem_v2
    _v28_value = _elem_v1
    _M_ub[_v28_key].remove(_v28_value)
    if (len(_M_ub[_v28_key]) == 0):
        del _M_ub[_v28_key]

def _maint_R_Q1_bu_for_R_Q1_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v29_key = _elem_v1
    _v29_value = _elem_v2
    if (_v29_key not in R_Q1_bu):
        _v30 = Set()
        R_Q1_bu[_v29_key] = _v30
    R_Q1_bu[_v29_key].add(_v29_value)

def _maint_R_Q1_bu_for_R_Q1_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v31_key = _elem_v1
    _v31_value = _elem_v2
    R_Q1_bu[_v31_key].remove(_v31_value)
    if (len(R_Q1_bu[_v31_key]) == 0):
        del R_Q1_bu[_v31_key]

def _maint_R_Q2_bbu_for_R_Q2_add(_elem):
    (_elem_v1, _elem_v2, _elem_v3) = _elem
    _v32_key = (_elem_v1, _elem_v2)
    _v32_value = _elem_v3
    if (_v32_key not in R_Q2_bbu):
        _v33 = Set()
        R_Q2_bbu[_v32_key] = _v33
    R_Q2_bbu[_v32_key].add(_v32_value)

def _maint_R_Q2_bbu_for_R_Q2_remove(_elem):
    (_elem_v1, _elem_v2, _elem_v3) = _elem
    _v34_key = (_elem_v1, _elem_v2)
    _v34_value = _elem_v3
    R_Q2_bbu[_v34_key].remove(_v34_value)
    if (len(R_Q2_bbu[_v34_key]) == 0):
        del R_Q2_bbu[_v34_key]

def _maint_R_Q2_for__U_Q2_add(_elem):
    (_v14_s, _v14_t) = _elem
    if isset(_v14_s):
        for _v14_o in _v14_s:
            if isset(_v14_t):
                if (_v14_o in _v14_t):
                    if hasfield(_v14_o, 'f'):
                        _v14_o_f = _v14_o.f
                        _v14_result = (_v14_s, _v14_t, _v14_o_f)
                        if (_v14_result not in R_Q2):
                            R_Q2.add(_v14_result)
                            _maint_R_Q2_bbu_for_R_Q2_add(_v14_result)
                        else:
                            R_Q2.inccount(_v14_result)

def _maint_R_Q2_for__U_Q2_remove(_elem):
    (_v15_s, _v15_t) = _elem
    if isset(_v15_s):
        for _v15_o in _v15_s:
            if isset(_v15_t):
                if (_v15_o in _v15_t):
                    if hasfield(_v15_o, 'f'):
                        _v15_o_f = _v15_o.f
                        _v15_result = (_v15_s, _v15_t, _v15_o_f)
                        if (R_Q2.getcount(_v15_result) == 1):
                            _maint_R_Q2_bbu_for_R_Q2_remove(_v15_result)
                            R_Q2.remove(_v15_result)
                        else:
                            R_Q2.deccount(_v15_result)

def _maint_R_Q2_for__M_add(_elem):
    (_v16_s, _v16_o) = _elem
    if hasfield(_v16_o, 'f'):
        _v16_o_f = _v16_o.f
        for _v16_t in (_U_Q2_bu[_v16_s] if (_v16_s in _U_Q2_bu) else ()):
            if isset(_v16_t):
                if (_v16_o in _v16_t):
                    if ((_v16_t, _v16_o) != _elem):
                        _v16_result = (_v16_s, _v16_t, _v16_o_f)
                        if (_v16_result not in R_Q2):
                            R_Q2.add(_v16_result)
                            _maint_R_Q2_bbu_for_R_Q2_add(_v16_result)
                        else:
                            R_Q2.inccount(_v16_result)
    (_v16_t, _v16_o) = _elem
    if hasfield(_v16_o, 'f'):
        _v16_o_f = _v16_o.f
        for _v16_s in (_U_Q2_ub[_v16_t] if (_v16_t in _U_Q2_ub) else ()):
            if isset(_v16_s):
                if (_v16_o in _v16_s):
                    _v16_result = (_v16_s, _v16_t, _v16_o_f)
                    if (_v16_result not in R_Q2):
                        R_Q2.add(_v16_result)
                        _maint_R_Q2_bbu_for_R_Q2_add(_v16_result)
                    else:
                        R_Q2.inccount(_v16_result)

def _maint_R_Q2_for__M_remove(_elem):
    (_v17_s, _v17_o) = _elem
    if hasfield(_v17_o, 'f'):
        _v17_o_f = _v17_o.f
        for _v17_t in (_U_Q2_bu[_v17_s] if (_v17_s in _U_Q2_bu) else ()):
            if isset(_v17_t):
                if (_v17_o in _v17_t):
                    if ((_v17_t, _v17_o) != _elem):
                        _v17_result = (_v17_s, _v17_t, _v17_o_f)
                        if (R_Q2.getcount(_v17_result) == 1):
                            _maint_R_Q2_bbu_for_R_Q2_remove(_v17_result)
                            R_Q2.remove(_v17_result)
                        else:
                            R_Q2.deccount(_v17_result)
    (_v17_t, _v17_o) = _elem
    if hasfield(_v17_o, 'f'):
        _v17_o_f = _v17_o.f
        for _v17_s in (_U_Q2_ub[_v17_t] if (_v17_t in _U_Q2_ub) else ()):
            if isset(_v17_s):
                if (_v17_o in _v17_s):
                    _v17_result = (_v17_s, _v17_t, _v17_o_f)
                    if (R_Q2.getcount(_v17_result) == 1):
                        _maint_R_Q2_bbu_for_R_Q2_remove(_v17_result)
                        R_Q2.remove(_v17_result)
                    else:
                        R_Q2.deccount(_v17_result)

def _maint_R_Q2_for__F_f_add(_elem):
    (_v18_o, _v18_o_f) = _elem
    for _v18_s in (_M_ub[_v18_o] if (_v18_o in _M_ub) else ()):
        for _v18_t in (_U_Q2_bu[_v18_s] if (_v18_s in _U_Q2_bu) else ()):
            if isset(_v18_t):
                if (_v18_o in _v18_t):
                    _v18_result = (_v18_s, _v18_t, _v18_o_f)
                    if (_v18_result not in R_Q2):
                        R_Q2.add(_v18_result)
                        _maint_R_Q2_bbu_for_R_Q2_add(_v18_result)
                    else:
                        R_Q2.inccount(_v18_result)

def _maint_R_Q2_for__F_f_remove(_elem):
    (_v19_o, _v19_o_f) = _elem
    for _v19_s in (_M_ub[_v19_o] if (_v19_o in _M_ub) else ()):
        for _v19_t in (_U_Q2_bu[_v19_s] if (_v19_s in _U_Q2_bu) else ()):
            if isset(_v19_t):
                if (_v19_o in _v19_t):
                    _v19_result = (_v19_s, _v19_t, _v19_o_f)
                    if (R_Q2.getcount(_v19_result) == 1):
                        _maint_R_Q2_bbu_for_R_Q2_remove(_v19_result)
                        R_Q2.remove(_v19_result)
                    else:
                        R_Q2.deccount(_v19_result)

def _maint_R_Q1_for__U_Q1_add(_elem):
    (_v8_z,) = _elem
    if isset(_v8_z):
        for _v8_o in _v8_z:
            if hasfield(_v8_o, 'f'):
                _v8_o_f = _v8_o.f
                _v8_result = (_v8_z, _v8_o_f)
                if (_v8_result not in R_Q1):
                    R_Q1.add(_v8_result)
                    _maint_R_Q1_bu_for_R_Q1_add(_v8_result)
                else:
                    R_Q1.inccount(_v8_result)

def _maint_R_Q1_for__U_Q1_remove(_elem):
    (_v9_z,) = _elem
    if isset(_v9_z):
        for _v9_o in _v9_z:
            if hasfield(_v9_o, 'f'):
                _v9_o_f = _v9_o.f
                _v9_result = (_v9_z, _v9_o_f)
                if (R_Q1.getcount(_v9_result) == 1):
                    _maint_R_Q1_bu_for_R_Q1_remove(_v9_result)
                    R_Q1.remove(_v9_result)
                else:
                    R_Q1.deccount(_v9_result)

def _maint_R_Q1_for__M_add(_elem):
    (_v10_z, _v10_o) = _elem
    if ((_v10_z,) in _U_Q1):
        if hasfield(_v10_o, 'f'):
            _v10_o_f = _v10_o.f
            _v10_result = (_v10_z, _v10_o_f)
            if (_v10_result not in R_Q1):
                R_Q1.add(_v10_result)
                _maint_R_Q1_bu_for_R_Q1_add(_v10_result)
            else:
                R_Q1.inccount(_v10_result)

def _maint_R_Q1_for__M_remove(_elem):
    (_v11_z, _v11_o) = _elem
    if ((_v11_z,) in _U_Q1):
        if hasfield(_v11_o, 'f'):
            _v11_o_f = _v11_o.f
            _v11_result = (_v11_z, _v11_o_f)
            if (R_Q1.getcount(_v11_result) == 1):
                _maint_R_Q1_bu_for_R_Q1_remove(_v11_result)
                R_Q1.remove(_v11_result)
            else:
                R_Q1.deccount(_v11_result)

def _maint_R_Q1_for__F_f_add(_elem):
    (_v12_o, _v12_o_f) = _elem
    for _v12_z in (_M_ub[_v12_o] if (_v12_o in _M_ub) else ()):
        if ((_v12_z,) in _U_Q1):
            _v12_result = (_v12_z, _v12_o_f)
            if (_v12_result not in R_Q1):
                R_Q1.add(_v12_result)
                _maint_R_Q1_bu_for_R_Q1_add(_v12_result)
            else:
                R_Q1.inccount(_v12_result)

def _maint_R_Q1_for__F_f_remove(_elem):
    (_v13_o, _v13_o_f) = _elem
    for _v13_z in (_M_ub[_v13_o] if (_v13_o in _M_ub) else ()):
        if ((_v13_z,) in _U_Q1):
            _v13_result = (_v13_z, _v13_o_f)
            if (R_Q1.getcount(_v13_result) == 1):
                _maint_R_Q1_bu_for_R_Q1_remove(_v13_result)
                R_Q1.remove(_v13_result)
            else:
                R_Q1.deccount(_v13_result)

def _demand_Q1(_elem):
    if (_elem not in _U_Q1):
        _U_Q1.add(_elem)
        _maint_R_Q1_for__U_Q1_add(_elem)

def _demand_Q2(_elem):
    if (_elem not in _U_Q2):
        _U_Q2.add(_elem)
        _maint__U_Q2_bu_for__U_Q2_add(_elem)
        _maint__U_Q2_ub_for__U_Q2_add(_elem)
        _maint_R_Q2_for__U_Q2_add(_elem)

def main():
    s = Set()
    t = Set()
    for i in [1, 2, 3, 4]:
        p = Obj()
        _v2 = (p, i)
        index(_v2, 0).f = index(_v2, 1)
        _maint_R_Q2_for__F_f_add(_v2)
        _maint_R_Q1_for__F_f_add(_v2)
        r = (s if (i % 2) else t)
        _v3 = (r, p)
        index(_v3, 0).add(index(_v3, 1))
        _maint__M_ub_for__M_add(_v3)
        _maint_R_Q2_for__M_add(_v3)
        _maint_R_Q1_for__M_add(_v3)
    p = Obj()
    _v4 = (p, 5)
    index(_v4, 0).f = index(_v4, 1)
    _maint_R_Q2_for__F_f_add(_v4)
    _maint_R_Q1_for__F_f_add(_v4)
    _v5 = (s, p)
    index(_v5, 0).add(index(_v5, 1))
    _maint__M_ub_for__M_add(_v5)
    _maint_R_Q2_for__M_add(_v5)
    _maint_R_Q1_for__M_add(_v5)
    _v6 = (t, p)
    index(_v6, 0).add(index(_v6, 1))
    _maint__M_ub_for__M_add(_v6)
    _maint_R_Q2_for__M_add(_v6)
    _maint_R_Q1_for__M_add(_v6)
    z = s
    print(sorted(((_demand_Q1((z,)) or True) and (R_Q1_bu[z] if (z in R_Q1_bu) else Set()))))
    z = t
    print(sorted(((_demand_Q1((z,)) or True) and (R_Q1_bu[z] if (z in R_Q1_bu) else Set()))))
    print(sorted(((_demand_Q2((s, t)) or True) and (R_Q2_bbu[(s, t)] if ((s, t) in R_Q2_bbu) else Set()))))
    for _v1 in list(t):
        _v7 = (t, _v1)
        _maint_R_Q1_for__M_remove(_v7)
        _maint_R_Q2_for__M_remove(_v7)
        _maint__M_ub_for__M_remove(_v7)
        index(_v7, 0).remove(index(_v7, 1))
    print(sorted(((_demand_Q2((s, t)) or True) and (R_Q2_bbu[(s, t)] if ((s, t) in R_Q2_bbu) else Set()))))

if (__name__ == '__main__'):
    main()
