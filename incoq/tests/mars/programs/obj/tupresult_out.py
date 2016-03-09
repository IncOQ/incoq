# Q1 : s -> {(s, (x, y)) for (s,) in REL(R__QU_Q1) for (s, t_x_y) in M() for (t_x_y, x, y) in TUP()} : {({(Number, Number)}, (Bottom, Bottom))}
# Q2 : s -> {(s, z) for (s,) in REL(_U_Q2) for (s, z) in REL(R_Q1)} : {({(Number, Number)}, (Bottom, Bottom))}
# _QU_Q1 : {(_v2s,) for (_v2s,) in REL(_U_Q2)} : {({(Number, Number)})}
from incoq.mars.runtime import *
# _M : {(Top, Top)}
_M = Set()
# _TUP_2 : {(Top, Top, Top)}
_TUP_2 = Set()
# _U_Q2 : {({(Number, Number)})}
_U_Q2 = Set()
# R__QU_Q1 : {({(Number, Number)})}
R__QU_Q1 = CSet()
# R_Q1 : {({(Number, Number)}, (Bottom, Bottom))}
R_Q1 = CSet()
# R_Q2 : {({(Number, Number)}, (Bottom, Bottom))}
R_Q2 = CSet()
# R_Q1_bu : {{(Number, Number)}: {(Bottom, Bottom)}}
R_Q1_bu = Map()
# _M_ub : {Top: {Top}}
_M_ub = Map()
# R_Q2_bu : {{(Number, Number)}: {(Bottom, Bottom)}}
R_Q2_bu = Map()
def _maint_R_Q1_bu_for_R_Q1_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v15_key = _elem_v1
    _v15_value = _elem_v2
    if (_v15_key not in R_Q1_bu):
        _v16 = Set()
        R_Q1_bu[_v15_key] = _v16
    R_Q1_bu[_v15_key].add(_v15_value)

def _maint_R_Q1_bu_for_R_Q1_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v17_key = _elem_v1
    _v17_value = _elem_v2
    R_Q1_bu[_v17_key].remove(_v17_value)
    if (len(R_Q1_bu[_v17_key]) == 0):
        del R_Q1_bu[_v17_key]

def _maint__M_ub_for__M_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v18_key = _elem_v2
    _v18_value = _elem_v1
    if (_v18_key not in _M_ub):
        _v19 = Set()
        _M_ub[_v18_key] = _v19
    _M_ub[_v18_key].add(_v18_value)

def _maint__M_ub_for__M_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v20_key = _elem_v2
    _v20_value = _elem_v1
    _M_ub[_v20_key].remove(_v20_value)
    if (len(_M_ub[_v20_key]) == 0):
        del _M_ub[_v20_key]

def _maint_R_Q2_bu_for_R_Q2_add(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v21_key = _elem_v1
    _v21_value = _elem_v2
    if (_v21_key not in R_Q2_bu):
        _v22 = Set()
        R_Q2_bu[_v21_key] = _v22
    R_Q2_bu[_v21_key].add(_v21_value)

def _maint_R_Q2_bu_for_R_Q2_remove(_elem):
    (_elem_v1, _elem_v2) = _elem
    _v23_key = _elem_v1
    _v23_value = _elem_v2
    R_Q2_bu[_v23_key].remove(_v23_value)
    if (len(R_Q2_bu[_v23_key]) == 0):
        del R_Q2_bu[_v23_key]

def _maint_R_Q2_for__U_Q2_add(_elem):
    (_v11_s,) = _elem
    for _v11_z in R_Q1_bu.get(_v11_s, Set()):
        _v11_result = (_v11_s, _v11_z)
        if (_v11_result not in R_Q2):
            R_Q2.add(_v11_result)
            _maint_R_Q2_bu_for_R_Q2_add(_v11_result)
        else:
            R_Q2.inccount(_v11_result)

def _maint_R_Q2_for__U_Q2_remove(_elem):
    (_v12_s,) = _elem
    for _v12_z in R_Q1_bu.get(_v12_s, Set()):
        _v12_result = (_v12_s, _v12_z)
        if (R_Q2.getcount(_v12_result) == 1):
            _maint_R_Q2_bu_for_R_Q2_remove(_v12_result)
            R_Q2.remove(_v12_result)
        else:
            R_Q2.deccount(_v12_result)

def _maint_R_Q2_for_R_Q1_add(_elem):
    (_v13_s, _v13_z) = _elem
    if ((_v13_s,) in _U_Q2):
        _v13_result = (_v13_s, _v13_z)
        if (_v13_result not in R_Q2):
            R_Q2.add(_v13_result)
            _maint_R_Q2_bu_for_R_Q2_add(_v13_result)
        else:
            R_Q2.inccount(_v13_result)

def _maint_R_Q2_for_R_Q1_remove(_elem):
    (_v14_s, _v14_z) = _elem
    if ((_v14_s,) in _U_Q2):
        _v14_result = (_v14_s, _v14_z)
        if (R_Q2.getcount(_v14_result) == 1):
            _maint_R_Q2_bu_for_R_Q2_remove(_v14_result)
            R_Q2.remove(_v14_result)
        else:
            R_Q2.deccount(_v14_result)

def _maint_R_Q1_for_R__QU_Q1_add(_elem):
    (_v5_s,) = _elem
    if isset(_v5_s):
        for _v5_t_x_y in _v5_s:
            if hasarity(_v5_t_x_y, 2):
                (_v5_x, _v5_y) = _v5_t_x_y
                _v5_result = (_v5_s, (_v5_x, _v5_y))
                if (_v5_result not in R_Q1):
                    R_Q1.add(_v5_result)
                    _maint_R_Q1_bu_for_R_Q1_add(_v5_result)
                    _maint_R_Q2_for_R_Q1_add(_v5_result)
                else:
                    R_Q1.inccount(_v5_result)

def _maint_R_Q1_for_R__QU_Q1_remove(_elem):
    (_v6_s,) = _elem
    if isset(_v6_s):
        for _v6_t_x_y in _v6_s:
            if hasarity(_v6_t_x_y, 2):
                (_v6_x, _v6_y) = _v6_t_x_y
                _v6_result = (_v6_s, (_v6_x, _v6_y))
                if (R_Q1.getcount(_v6_result) == 1):
                    _maint_R_Q2_for_R_Q1_remove(_v6_result)
                    _maint_R_Q1_bu_for_R_Q1_remove(_v6_result)
                    R_Q1.remove(_v6_result)
                else:
                    R_Q1.deccount(_v6_result)

def _maint_R_Q1_for__M_add(_elem):
    (_v7_s, _v7_t_x_y) = _elem
    if ((_v7_s,) in R__QU_Q1):
        if hasarity(_v7_t_x_y, 2):
            (_v7_x, _v7_y) = _v7_t_x_y
            _v7_result = (_v7_s, (_v7_x, _v7_y))
            if (_v7_result not in R_Q1):
                R_Q1.add(_v7_result)
                _maint_R_Q1_bu_for_R_Q1_add(_v7_result)
                _maint_R_Q2_for_R_Q1_add(_v7_result)
            else:
                R_Q1.inccount(_v7_result)

def _maint_R_Q1_for__M_remove(_elem):
    (_v8_s, _v8_t_x_y) = _elem
    if ((_v8_s,) in R__QU_Q1):
        if hasarity(_v8_t_x_y, 2):
            (_v8_x, _v8_y) = _v8_t_x_y
            _v8_result = (_v8_s, (_v8_x, _v8_y))
            if (R_Q1.getcount(_v8_result) == 1):
                _maint_R_Q2_for_R_Q1_remove(_v8_result)
                _maint_R_Q1_bu_for_R_Q1_remove(_v8_result)
                R_Q1.remove(_v8_result)
            else:
                R_Q1.deccount(_v8_result)

def _maint_R_Q1_for__TUP_2_add(_elem):
    (_v9_t_x_y, _v9_x, _v9_y) = _elem
    for _v9_s in _M_ub.get(_v9_t_x_y, Set()):
        if ((_v9_s,) in R__QU_Q1):
            _v9_result = (_v9_s, (_v9_x, _v9_y))
            if (_v9_result not in R_Q1):
                R_Q1.add(_v9_result)
                _maint_R_Q1_bu_for_R_Q1_add(_v9_result)
                _maint_R_Q2_for_R_Q1_add(_v9_result)
            else:
                R_Q1.inccount(_v9_result)

def _maint_R_Q1_for__TUP_2_remove(_elem):
    (_v10_t_x_y, _v10_x, _v10_y) = _elem
    for _v10_s in _M_ub.get(_v10_t_x_y, Set()):
        if ((_v10_s,) in R__QU_Q1):
            _v10_result = (_v10_s, (_v10_x, _v10_y))
            if (R_Q1.getcount(_v10_result) == 1):
                _maint_R_Q2_for_R_Q1_remove(_v10_result)
                _maint_R_Q1_bu_for_R_Q1_remove(_v10_result)
                R_Q1.remove(_v10_result)
            else:
                R_Q1.deccount(_v10_result)

def _maint_R__QU_Q1_for__U_Q2_add(_elem):
    (_v3__v2s,) = _elem
    _v3_result = (_v3__v2s,)
    if (_v3_result not in R__QU_Q1):
        R__QU_Q1.add(_v3_result)
        _maint_R_Q1_for_R__QU_Q1_add(_v3_result)
    else:
        R__QU_Q1.inccount(_v3_result)

def _maint_R__QU_Q1_for__U_Q2_remove(_elem):
    (_v4__v2s,) = _elem
    _v4_result = (_v4__v2s,)
    if (R__QU_Q1.getcount(_v4_result) == 1):
        _maint_R_Q1_for_R__QU_Q1_remove(_v4_result)
        R__QU_Q1.remove(_v4_result)
    else:
        R__QU_Q1.deccount(_v4_result)

def _demand_Q2(_elem):
    if (_elem not in _U_Q2):
        _U_Q2.add(_elem)
        _maint_R_Q2_for__U_Q2_add(_elem)
        _maint_R__QU_Q1_for__U_Q2_add(_elem)

def main():
    s = Set()
    for e in [(1, 2), (3, 4)]:
        _v1 = (s, e)
        index(_v1, 0).add(index(_v1, 1))
        _maint__M_ub_for__M_add(_v1)
        _maint_R_Q1_for__M_add(_v1)
    print(sorted(((_demand_Q2((s,)) or True) and R_Q2_bu.get(s, Set()))))

if (__name__ == '__main__'):
    main()
