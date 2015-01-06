from oinc.runtime import *
# Comp1 := {(a, b, c) : a in _U_Comp1, (a, b, c) in R}
_m_Comp1_bbu = Map()
def _maint__m_Comp1_bbu_add(_e):
    (v7_1, v7_2, v7_3) = _e
    if ((v7_1, v7_2) not in _m_Comp1_bbu):
        _m_Comp1_bbu[(v7_1, v7_2)] = set()
    _m_Comp1_bbu[(v7_1, v7_2)].add(v7_3)

def _maint__m_Comp1_bbu_remove(_e):
    (v8_1, v8_2, v8_3) = _e
    _m_Comp1_bbu[(v8_1, v8_2)].remove(v8_3)
    if (len(_m_Comp1_bbu[(v8_1, v8_2)]) == 0):
        del _m_Comp1_bbu[(v8_1, v8_2)]

_m_R_buu = Map()
def _maint__m_R_buu_add(_e):
    (v5_1, v5_2, v5_3) = _e
    if (v5_1 not in _m_R_buu):
        _m_R_buu[v5_1] = set()
    _m_R_buu[v5_1].add((v5_2, v5_3))

def _maint_Comp1__U_Comp1_add(_e):
    # Iterate {(v1_a, v1_b, v1_c) : v1_a in deltamatch(_U_Comp1, 'b', _e, 1), (v1_a, v1_b, v1_c) in R}
    v1_a = _e
    for (v1_b, v1_c) in (_m_R_buu[v1_a] if (v1_a in _m_R_buu) else set()):
        # Begin maint _m_Comp1_bbu after "Comp1.add((v1_a, v1_b, v1_c))"
        _maint__m_Comp1_bbu_add((v1_a, v1_b, v1_c))
        # End maint _m_Comp1_bbu after "Comp1.add((v1_a, v1_b, v1_c))"

def _maint_Comp1__U_Comp1_remove(_e):
    # Iterate {(v2_a, v2_b, v2_c) : v2_a in deltamatch(_U_Comp1, 'b', _e, 1), (v2_a, v2_b, v2_c) in R}
    v2_a = _e
    for (v2_b, v2_c) in (_m_R_buu[v2_a] if (v2_a in _m_R_buu) else set()):
        # Begin maint _m_Comp1_bbu before "Comp1.remove((v2_a, v2_b, v2_c))"
        _maint__m_Comp1_bbu_remove((v2_a, v2_b, v2_c))
        # End maint _m_Comp1_bbu before "Comp1.remove((v2_a, v2_b, v2_c))"

def _maint_Comp1_R_add(_e):
    # Iterate {(v3_a, v3_b, v3_c) : v3_a in _U_Comp1, (v3_a, v3_b, v3_c) in deltamatch(R, 'bbb', _e, 1)}
    (v3_a, v3_b, v3_c) = _e
    if (v3_a in _U_Comp1):
        # Begin maint _m_Comp1_bbu after "Comp1.add((v3_a, v3_b, v3_c))"
        _maint__m_Comp1_bbu_add((v3_a, v3_b, v3_c))
        # End maint _m_Comp1_bbu after "Comp1.add((v3_a, v3_b, v3_c))"

_U_Comp1 = RCSet()
_UEXT_Comp1 = Set()
def demand_Comp1(a):
    '{(a, b, c) : a in _U_Comp1, (a, b, c) in R}'
    if (a not in _U_Comp1):
        _U_Comp1.add(a)
        # Begin maint Comp1 after "_U_Comp1.add(a)"
        _maint_Comp1__U_Comp1_add(a)
        # End maint Comp1 after "_U_Comp1.add(a)"
    else:
        _U_Comp1.incref(a)

def undemand_Comp1(a):
    '{(a, b, c) : a in _U_Comp1, (a, b, c) in R}'
    if (_U_Comp1.getref(a) == 1):
        # Begin maint Comp1 before "_U_Comp1.remove(a)"
        _maint_Comp1__U_Comp1_remove(a)
        # End maint Comp1 before "_U_Comp1.remove(a)"
        _U_Comp1.remove(a)
    else:
        _U_Comp1.decref(a)

def query_Comp1(a):
    '{(a, b, c) : a in _U_Comp1, (a, b, c) in R}'
    if (a not in _UEXT_Comp1):
        _UEXT_Comp1.add(a)
        demand_Comp1(a)
    return True

for (v1, v2, v3) in {(1, 2, 3), (2, 2, 3), (1, 3, 4)}:
    # Begin maint _m_R_buu after "R.add((v1, v2, v3))"
    _maint__m_R_buu_add((v1, v2, v3))
    # End maint _m_R_buu after "R.add((v1, v2, v3))"
    # Begin maint Comp1 after "R.add((v1, v2, v3))"
    _maint_Comp1_R_add((v1, v2, v3))
    # End maint Comp1 after "R.add((v1, v2, v3))"
a = 1
b = 2
print(sorted((query_Comp1(a) and (_m_Comp1_bbu[(a, b)] if ((a, b) in _m_Comp1_bbu) else set()))))