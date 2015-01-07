from invinc.runtime import *
# Comp1 := {(g, x) : g in _U_Comp1, x in E, (x > g)}
_m_Comp1_out = Map()
def _maint__m_Comp1_out_add(_e):
    (v5_1, v5_2) = _e
    if (v5_1 not in _m_Comp1_out):
        _m_Comp1_out[v5_1] = set()
    _m_Comp1_out[v5_1].add(v5_2)

def _maint__m_Comp1_out_remove(_e):
    (v6_1, v6_2) = _e
    _m_Comp1_out[v6_1].remove(v6_2)
    if (len(_m_Comp1_out[v6_1]) == 0):
        del _m_Comp1_out[v6_1]

def _maint_Comp1__U_Comp1_add(_e):
    # Iterate {(v1_g, v1_x) : v1_g in deltamatch(_U_Comp1, 'b', _e, 1), v1_x in E, (v1_x > v1_g)}
    v1_g = _e
    for v1_x in E:
        if (v1_x > v1_g):
            # Begin maint _m_Comp1_out after "Comp1.add((v1_g, v1_x))"
            _maint__m_Comp1_out_add((v1_g, v1_x))
            # End maint _m_Comp1_out after "Comp1.add((v1_g, v1_x))"

def _maint_Comp1__U_Comp1_remove(_e):
    # Iterate {(v2_g, v2_x) : v2_g in deltamatch(_U_Comp1, 'b', _e, 1), v2_x in E, (v2_x > v2_g)}
    v2_g = _e
    for v2_x in E:
        if (v2_x > v2_g):
            # Begin maint _m_Comp1_out before "Comp1.remove((v2_g, v2_x))"
            _maint__m_Comp1_out_remove((v2_g, v2_x))
            # End maint _m_Comp1_out before "Comp1.remove((v2_g, v2_x))"

def _maint_Comp1_E_add(_e):
    # Iterate {(v3_g, v3_x) : v3_g in _U_Comp1, v3_x in deltamatch(E, 'b', _e, 1), (v3_x > v3_g)}
    v3_x = _e
    for v3_g in _U_Comp1:
        if (v3_x > v3_g):
            # Begin maint _m_Comp1_out after "Comp1.add((v3_g, v3_x))"
            _maint__m_Comp1_out_add((v3_g, v3_x))
            # End maint _m_Comp1_out after "Comp1.add((v3_g, v3_x))"

_U_Comp1 = RCSet()
_UEXT_Comp1 = Set()
def demand_Comp1(g):
    '{(g, x) : g in _U_Comp1, x in E, (x > g)}'
    if (g not in _U_Comp1):
        _U_Comp1.add(g)
        # Begin maint Comp1 after "_U_Comp1.add(g)"
        _maint_Comp1__U_Comp1_add(g)
        # End maint Comp1 after "_U_Comp1.add(g)"
    else:
        _U_Comp1.incref(g)

def undemand_Comp1(g):
    '{(g, x) : g in _U_Comp1, x in E, (x > g)}'
    if (_U_Comp1.getref(g) == 1):
        # Begin maint Comp1 before "_U_Comp1.remove(g)"
        _maint_Comp1__U_Comp1_remove(g)
        # End maint Comp1 before "_U_Comp1.remove(g)"
        _U_Comp1.remove(g)
    else:
        _U_Comp1.decref(g)

def query_Comp1(g):
    '{(g, x) : g in _U_Comp1, x in E, (x > g)}'
    if (g not in _UEXT_Comp1):
        _UEXT_Comp1.add(g)
        demand_Comp1(g)
    return True

E = Set()
g = 1
for z in [1, 2, 3]:
    E.add(z)
    # Begin maint Comp1 after "E.add(z)"
    _maint_Comp1_E_add(z)
    # End maint Comp1 after "E.add(z)"
print(sorted((query_Comp1(g) and (_m_Comp1_out[g] if (g in _m_Comp1_out) else set()))))