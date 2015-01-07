from invinc.runtime import *
# Comp1 := {(x, z) : x in _U_Comp1, (x, y) in E, (y, z) in E}
_m_Comp1_out = Map()
def _maint__m_Comp1_out_add(_e):
    (v9_1, v9_2) = _e
    if (v9_1 not in _m_Comp1_out):
        _m_Comp1_out[v9_1] = set()
    _m_Comp1_out[v9_1].add(v9_2)

def _maint__m_Comp1_out_remove(_e):
    (v10_1, v10_2) = _e
    _m_Comp1_out[v10_1].remove(v10_2)
    if (len(_m_Comp1_out[v10_1]) == 0):
        del _m_Comp1_out[v10_1]

_m_E_in = Map()
def _maint__m_E_in_add(_e):
    (v7_1, v7_2) = _e
    if (v7_2 not in _m_E_in):
        _m_E_in[v7_2] = set()
    _m_E_in[v7_2].add(v7_1)

_m_E_out = Map()
def _maint__m_E_out_add(_e):
    (v5_1, v5_2) = _e
    if (v5_1 not in _m_E_out):
        _m_E_out[v5_1] = set()
    _m_E_out[v5_1].add(v5_2)

Comp1 = RCSet()
def _maint_Comp1__U_Comp1_add(_e):
    # Iterate {(v1_x, v1_y, v1_z) : v1_x in deltamatch(_U_Comp1, 'b', _e, 1), (v1_x, v1_y) in E, (v1_y, v1_z) in E}
    v1_x = _e
    for v1_y in (_m_E_out[v1_x] if (v1_x in _m_E_out) else set()):
        for v1_z in (_m_E_out[v1_y] if (v1_y in _m_E_out) else set()):
            if ((v1_x, v1_z) not in Comp1):
                Comp1.add((v1_x, v1_z))
                # Begin maint _m_Comp1_out after "Comp1.add((v1_x, v1_z))"
                _maint__m_Comp1_out_add((v1_x, v1_z))
                # End maint _m_Comp1_out after "Comp1.add((v1_x, v1_z))"
            else:
                Comp1.incref((v1_x, v1_z))

def _maint_Comp1__U_Comp1_remove(_e):
    # Iterate {(v2_x, v2_y, v2_z) : v2_x in deltamatch(_U_Comp1, 'b', _e, 1), (v2_x, v2_y) in E, (v2_y, v2_z) in E}
    v2_x = _e
    for v2_y in (_m_E_out[v2_x] if (v2_x in _m_E_out) else set()):
        for v2_z in (_m_E_out[v2_y] if (v2_y in _m_E_out) else set()):
            if (Comp1.getref((v2_x, v2_z)) == 1):
                # Begin maint _m_Comp1_out before "Comp1.remove((v2_x, v2_z))"
                _maint__m_Comp1_out_remove((v2_x, v2_z))
                # End maint _m_Comp1_out before "Comp1.remove((v2_x, v2_z))"
                Comp1.remove((v2_x, v2_z))
            else:
                Comp1.decref((v2_x, v2_z))

def _maint_Comp1_E_add(_e):
    v3_DAS = set()
    # Iterate {(v3_x, v3_y, v3_z) : v3_x in _U_Comp1, (v3_x, v3_y) in deltamatch(E, 'bb', _e, 1), (v3_y, v3_z) in E}
    (v3_x, v3_y) = _e
    if (v3_x in _U_Comp1):
        for v3_z in (_m_E_out[v3_y] if (v3_y in _m_E_out) else set()):
            if ((v3_x, v3_y, v3_z) not in v3_DAS):
                v3_DAS.add((v3_x, v3_y, v3_z))
    # Iterate {(v3_x, v3_y, v3_z) : v3_x in _U_Comp1, (v3_x, v3_y) in E, (v3_y, v3_z) in deltamatch(E, 'bb', _e, 1)}
    (v3_y, v3_z) = _e
    for v3_x in (_m_E_in[v3_y] if (v3_y in _m_E_in) else set()):
        if (v3_x in _U_Comp1):
            if ((v3_x, v3_y, v3_z) not in v3_DAS):
                v3_DAS.add((v3_x, v3_y, v3_z))
    for (v3_x, v3_y, v3_z) in v3_DAS:
        if ((v3_x, v3_z) not in Comp1):
            Comp1.add((v3_x, v3_z))
            # Begin maint _m_Comp1_out after "Comp1.add((v3_x, v3_z))"
            _maint__m_Comp1_out_add((v3_x, v3_z))
            # End maint _m_Comp1_out after "Comp1.add((v3_x, v3_z))"
        else:
            Comp1.incref((v3_x, v3_z))
    del v3_DAS

_U_Comp1 = RCSet()
_UEXT_Comp1 = Set()
def demand_Comp1(x):
    '{(x, z) : x in _U_Comp1, (x, y) in E, (y, z) in E}'
    if (x not in _U_Comp1):
        _U_Comp1.add(x)
        # Begin maint Comp1 after "_U_Comp1.add(x)"
        _maint_Comp1__U_Comp1_add(x)
        # End maint Comp1 after "_U_Comp1.add(x)"
    else:
        _U_Comp1.incref(x)

def undemand_Comp1(x):
    '{(x, z) : x in _U_Comp1, (x, y) in E, (y, z) in E}'
    if (_U_Comp1.getref(x) == 1):
        # Begin maint Comp1 before "_U_Comp1.remove(x)"
        _maint_Comp1__U_Comp1_remove(x)
        # End maint Comp1 before "_U_Comp1.remove(x)"
        _U_Comp1.remove(x)
    else:
        _U_Comp1.decref(x)

def query_Comp1(x):
    '{(x, z) : x in _U_Comp1, (x, y) in E, (y, z) in E}'
    if (x not in _UEXT_Comp1):
        _UEXT_Comp1.add(x)
        demand_Comp1(x)
    return True

for (a, b) in {(1, 2), (2, 3), (2, 4)}:
    # Begin maint _m_E_in after "E.add((a, b))"
    _maint__m_E_in_add((a, b))
    # End maint _m_E_in after "E.add((a, b))"
    # Begin maint _m_E_out after "E.add((a, b))"
    _maint__m_E_out_add((a, b))
    # End maint _m_E_out after "E.add((a, b))"
    # Begin maint Comp1 after "E.add((a, b))"
    _maint_Comp1_E_add((a, b))
    # End maint Comp1 after "E.add((a, b))"
x = 1
print(sorted((query_Comp1(x) and (_m_Comp1_out[x] if (x in _m_Comp1_out) else set()))))
print(sorted((_m_Comp1_out[x] if (x in _m_Comp1_out) else set())))