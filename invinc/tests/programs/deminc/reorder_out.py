from invinc.runtime import *
# Comp1 := {(z, x) : (x, y) in E, (y, z) in E}
# Comp1_Ty2 := {y : (y, z) in E}
# Comp1_dE1 := {(x, y) : y in Comp1_Ty2, (x, y) in E}
_m_Comp1_out = Map()
def _maint__m_Comp1_out_add(_e):
    (v15_1, v15_2) = _e
    if (v15_1 not in _m_Comp1_out):
        _m_Comp1_out[v15_1] = set()
    _m_Comp1_out[v15_1].add(v15_2)

def _maint__m_Comp1_out_remove(_e):
    (v16_1, v16_2) = _e
    _m_Comp1_out[v16_1].remove(v16_2)
    if (len(_m_Comp1_out[v16_1]) == 0):
        del _m_Comp1_out[v16_1]

_m_Comp1_dE1_in = Map()
def _maint__m_Comp1_dE1_in_add(_e):
    (v13_1, v13_2) = _e
    if (v13_2 not in _m_Comp1_dE1_in):
        _m_Comp1_dE1_in[v13_2] = set()
    _m_Comp1_dE1_in[v13_2].add(v13_1)

def _maint__m_Comp1_dE1_in_remove(_e):
    (v14_1, v14_2) = _e
    _m_Comp1_dE1_in[v14_2].remove(v14_1)
    if (len(_m_Comp1_dE1_in[v14_2]) == 0):
        del _m_Comp1_dE1_in[v14_2]

_m_E_out = Map()
def _maint__m_E_out_add(_e):
    (v11_1, v11_2) = _e
    if (v11_1 not in _m_E_out):
        _m_E_out[v11_1] = set()
    _m_E_out[v11_1].add(v11_2)

_m_E_in = Map()
def _maint__m_E_in_add(_e):
    (v9_1, v9_2) = _e
    if (v9_2 not in _m_E_in):
        _m_E_in[v9_2] = set()
    _m_E_in[v9_2].add(v9_1)

Comp1_dE1 = RCSet()
def _maint_Comp1_dE1_Comp1_Ty2_add(_e):
    # Iterate {(v5_y, v5_x) : v5_y in deltamatch(Comp1_Ty2, 'b', _e, 1), (v5_x, v5_y) in E}
    v5_y = _e
    for v5_x in (_m_E_in[v5_y] if (v5_y in _m_E_in) else set()):
        Comp1_dE1.add((v5_x, v5_y))
        # Begin maint _m_Comp1_dE1_in after "Comp1_dE1.add((v5_x, v5_y))"
        _maint__m_Comp1_dE1_in_add((v5_x, v5_y))
        # End maint _m_Comp1_dE1_in after "Comp1_dE1.add((v5_x, v5_y))"

def _maint_Comp1_dE1_Comp1_Ty2_remove(_e):
    # Iterate {(v6_y, v6_x) : v6_y in deltamatch(Comp1_Ty2, 'b', _e, 1), (v6_x, v6_y) in E}
    v6_y = _e
    for v6_x in (_m_E_in[v6_y] if (v6_y in _m_E_in) else set()):
        # Begin maint _m_Comp1_dE1_in before "Comp1_dE1.remove((v6_x, v6_y))"
        _maint__m_Comp1_dE1_in_remove((v6_x, v6_y))
        # End maint _m_Comp1_dE1_in before "Comp1_dE1.remove((v6_x, v6_y))"
        Comp1_dE1.remove((v6_x, v6_y))

def _maint_Comp1_dE1_E_add(_e):
    # Iterate {(v7_y, v7_x) : v7_y in Comp1_Ty2, (v7_x, v7_y) in deltamatch(E, 'bb', _e, 1)}
    (v7_x, v7_y) = _e
    if (v7_y in Comp1_Ty2):
        Comp1_dE1.add((v7_x, v7_y))
        # Begin maint _m_Comp1_dE1_in after "Comp1_dE1.add((v7_x, v7_y))"
        _maint__m_Comp1_dE1_in_add((v7_x, v7_y))
        # End maint _m_Comp1_dE1_in after "Comp1_dE1.add((v7_x, v7_y))"

Comp1_Ty2 = RCSet()
def _maint_Comp1_Ty2_E_add(_e):
    # Iterate {(v3_y, v3_z) : (v3_y, v3_z) in deltamatch(E, 'bb', _e, 1)}
    (v3_y, v3_z) = _e
    if (v3_y not in Comp1_Ty2):
        Comp1_Ty2.add(v3_y)
        # Begin maint Comp1_dE1 after "Comp1_Ty2.add(v3_y)"
        _maint_Comp1_dE1_Comp1_Ty2_add(v3_y)
        # End maint Comp1_dE1 after "Comp1_Ty2.add(v3_y)"
    else:
        Comp1_Ty2.incref(v3_y)

Comp1 = RCSet()
def _maint_Comp1_E_add(_e):
    v1_DAS = set()
    # Iterate {(v1_x, v1_y, v1_z) : (v1_x, v1_y) in deltamatch(Comp1_dE1, 'bb', _e, 1), (v1_x, v1_y) in Comp1_dE1, (v1_y, v1_z) in E}
    (v1_x, v1_y) = _e
    if ((v1_x, v1_y) in Comp1_dE1):
        for v1_z in (_m_E_out[v1_y] if (v1_y in _m_E_out) else set()):
            if ((v1_x, v1_y, v1_z) not in v1_DAS):
                v1_DAS.add((v1_x, v1_y, v1_z))
    # Iterate {(v1_x, v1_y, v1_z) : (v1_x, v1_y) in Comp1_dE1, (v1_y, v1_z) in deltamatch(E, 'bb', _e, 1)}
    (v1_y, v1_z) = _e
    for v1_x in (_m_Comp1_dE1_in[v1_y] if (v1_y in _m_Comp1_dE1_in) else set()):
        if ((v1_x, v1_y, v1_z) not in v1_DAS):
            v1_DAS.add((v1_x, v1_y, v1_z))
    for (v1_x, v1_y, v1_z) in v1_DAS:
        if ((v1_z, v1_x) not in Comp1):
            Comp1.add((v1_z, v1_x))
            # Begin maint _m_Comp1_out after "Comp1.add((v1_z, v1_x))"
            _maint__m_Comp1_out_add((v1_z, v1_x))
            # End maint _m_Comp1_out after "Comp1.add((v1_z, v1_x))"
        else:
            Comp1.incref((v1_z, v1_x))
    del v1_DAS

for (a, b) in {(1, 3), (2, 3), (3, 4)}:
    # Begin maint _m_E_out after "E.add((a, b))"
    _maint__m_E_out_add((a, b))
    # End maint _m_E_out after "E.add((a, b))"
    # Begin maint _m_E_in after "E.add((a, b))"
    _maint__m_E_in_add((a, b))
    # End maint _m_E_in after "E.add((a, b))"
    # Begin maint Comp1_dE1 after "E.add((a, b))"
    _maint_Comp1_dE1_E_add((a, b))
    # End maint Comp1_dE1 after "E.add((a, b))"
    # Begin maint Comp1_Ty2 after "E.add((a, b))"
    _maint_Comp1_Ty2_E_add((a, b))
    # End maint Comp1_Ty2 after "E.add((a, b))"
    # Begin maint Comp1 after "E.add((a, b))"
    _maint_Comp1_E_add((a, b))
    # End maint Comp1 after "E.add((a, b))"
z = 4
print(sorted((_m_Comp1_out[z] if (z in _m_Comp1_out) else set())))