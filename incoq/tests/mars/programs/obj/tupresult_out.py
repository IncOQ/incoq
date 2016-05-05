# Q1 : s -> {(s, (x, y)) for (s,) in REL(R__QU_Q1) for (s, t_x_y) in M() for (t_x_y, x, y) in TUP()} : {({(Number, Number)}, (Bottom, Bottom))}
# Q2 : s -> {(s, z) for (s,) in REL(_U_Q2) for (s, z) in REL(R_Q1)} : {({(Number, Number)}, (Bottom, Bottom))}
# _QU_Q1 : {(_v2s,) for (_v2s,) in REL(_U_Q2)} : {({(Number, Number)})}
from incoq.mars.runtime import *
# _U_Q2 : {({(Number, Number)})}
_U_Q2 = Set()
# R__QU_Q1 : {({(Number, Number)})}
R__QU_Q1 = Set()
# R_Q1 : {({(Number, Number)}, (Bottom, Bottom))}
R_Q1 = CSet()
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
    for _v11_z in (R_Q1_bu[_v11_s] if (_v11_s in R_Q1_bu) else ()):
        _v11_result = (_v11_s, _v11_z)
        _maint_R_Q2_bu_for_R_Q2_add(_v11_result)

def _maint_R_Q2_for_R_Q1_add(_elem):
    (_v13_s, _v13_z) = _elem
    if ((_v13_s,) in _U_Q2):
        _v13_result = (_v13_s, _v13_z)
        _maint_R_Q2_bu_for_R_Q2_add(_v13_result)

def _maint_R_Q2_for_R_Q1_remove(_elem):
    (_v14_s, _v14_z) = _elem
    if ((_v14_s,) in _U_Q2):
        _v14_result = (_v14_s, _v14_z)
        _maint_R_Q2_bu_for_R_Q2_remove(_v14_result)

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

def _maint_R__QU_Q1_for__U_Q2_add(_elem):
    (_v3__v2s,) = _elem
    _v3_result = (_v3__v2s,)
    R__QU_Q1.add(_v3_result)
    _maint_R_Q1_for_R__QU_Q1_add(_v3_result)

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
    print(sorted(((_demand_Q2((s,)) or True) and (R_Q2_bu[s] if (s in R_Q2_bu) else Set()))))

if (__name__ == '__main__'):
    main()
