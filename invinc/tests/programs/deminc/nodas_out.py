from invinc.runtime import *
# Comp1 := {(x, z) : (x, y) in E, (y, z) in E}
# Comp1_Ty1 := {y : (x, y) in E}
# Comp1_dE2 := {(y, z) : y in Comp1_Ty1, (y, z) in E}
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

_m_E_in = Map()
def _maint__m_E_in_add(_e):
    (v13_1, v13_2) = _e
    if (v13_2 not in _m_E_in):
        _m_E_in[v13_2] = set()
    _m_E_in[v13_2].add(v13_1)

_m_Comp1_dE2_out = Map()
def _maint__m_Comp1_dE2_out_add(_e):
    (v11_1, v11_2) = _e
    if (v11_1 not in _m_Comp1_dE2_out):
        _m_Comp1_dE2_out[v11_1] = set()
    _m_Comp1_dE2_out[v11_1].add(v11_2)

def _maint__m_Comp1_dE2_out_remove(_e):
    (v12_1, v12_2) = _e
    _m_Comp1_dE2_out[v12_1].remove(v12_2)
    if (len(_m_Comp1_dE2_out[v12_1]) == 0):
        del _m_Comp1_dE2_out[v12_1]

_m_E_out = Map()
def _maint__m_E_out_add(_e):
    (v9_1, v9_2) = _e
    if (v9_1 not in _m_E_out):
        _m_E_out[v9_1] = set()
    _m_E_out[v9_1].add(v9_2)

Comp1_dE2 = RCSet()
def _maint_Comp1_dE2_Comp1_Ty1_add(_e):
    # Iterate {(v5_y, v5_z) : v5_y in deltamatch(Comp1_Ty1, 'b', _e, 1), (v5_y, v5_z) in E}
    v5_y = _e
    for v5_z in (_m_E_out[v5_y] if (v5_y in _m_E_out) else set()):
        Comp1_dE2.add((v5_y, v5_z))
        # Begin maint _m_Comp1_dE2_out after "Comp1_dE2.add((v5_y, v5_z))"
        _maint__m_Comp1_dE2_out_add((v5_y, v5_z))
        # End maint _m_Comp1_dE2_out after "Comp1_dE2.add((v5_y, v5_z))"

def _maint_Comp1_dE2_Comp1_Ty1_remove(_e):
    # Iterate {(v6_y, v6_z) : v6_y in deltamatch(Comp1_Ty1, 'b', _e, 1), (v6_y, v6_z) in E}
    v6_y = _e
    for v6_z in (_m_E_out[v6_y] if (v6_y in _m_E_out) else set()):
        # Begin maint _m_Comp1_dE2_out before "Comp1_dE2.remove((v6_y, v6_z))"
        _maint__m_Comp1_dE2_out_remove((v6_y, v6_z))
        # End maint _m_Comp1_dE2_out before "Comp1_dE2.remove((v6_y, v6_z))"
        Comp1_dE2.remove((v6_y, v6_z))

def _maint_Comp1_dE2_E_add(_e):
    # Iterate {(v7_y, v7_z) : v7_y in Comp1_Ty1, (v7_y, v7_z) in deltamatch(E, 'bb', _e, 1)}
    (v7_y, v7_z) = _e
    if (v7_y in Comp1_Ty1):
        Comp1_dE2.add((v7_y, v7_z))
        # Begin maint _m_Comp1_dE2_out after "Comp1_dE2.add((v7_y, v7_z))"
        _maint__m_Comp1_dE2_out_add((v7_y, v7_z))
        # End maint _m_Comp1_dE2_out after "Comp1_dE2.add((v7_y, v7_z))"

Comp1_Ty1 = RCSet()
def _maint_Comp1_Ty1_E_add(_e):
    # Iterate {(v3_x, v3_y) : (v3_x, v3_y) in deltamatch(E, 'bb', _e, 1)}
    (v3_x, v3_y) = _e
    if (v3_y not in Comp1_Ty1):
        Comp1_Ty1.add(v3_y)
        # Begin maint Comp1_dE2 after "Comp1_Ty1.add(v3_y)"
        _maint_Comp1_dE2_Comp1_Ty1_add(v3_y)
        # End maint Comp1_dE2 after "Comp1_Ty1.add(v3_y)"
    else:
        Comp1_Ty1.incref(v3_y)

Comp1 = RCSet()
def _maint_Comp1_E_add(_e):
    # Iterate {(v1_x, v1_y, v1_z) : (v1_x, v1_y) in deltamatch(E, 'bb', _e, 1), (v1_y, v1_z) in (Comp1_dE2 - {_e})}
    (v1_x, v1_y) = _e
    for v1_z in (_m_Comp1_dE2_out[v1_y] if (v1_y in _m_Comp1_dE2_out) else set()):
        if ((v1_y, v1_z) != _e):
            if ((v1_x, v1_z) not in Comp1):
                Comp1.add((v1_x, v1_z))
                # Begin maint _m_Comp1_out after "Comp1.add((v1_x, v1_z))"
                _maint__m_Comp1_out_add((v1_x, v1_z))
                # End maint _m_Comp1_out after "Comp1.add((v1_x, v1_z))"
            else:
                Comp1.incref((v1_x, v1_z))
    # Iterate {(v1_x, v1_y, v1_z) : (v1_x, v1_y) in E, (v1_y, v1_z) in deltamatch(Comp1_dE2, 'bb', _e, 1), (v1_y, v1_z) in Comp1_dE2}
    (v1_y, v1_z) = _e
    if ((v1_y, v1_z) in Comp1_dE2):
        for v1_x in (_m_E_in[v1_y] if (v1_y in _m_E_in) else set()):
            if ((v1_x, v1_z) not in Comp1):
                Comp1.add((v1_x, v1_z))
                # Begin maint _m_Comp1_out after "Comp1.add((v1_x, v1_z))"
                _maint__m_Comp1_out_add((v1_x, v1_z))
                # End maint _m_Comp1_out after "Comp1.add((v1_x, v1_z))"
            else:
                Comp1.incref((v1_x, v1_z))

for (a, b) in {(1, 2), (2, 3), (2, 4)}:
    # Begin maint _m_E_in after "E.add((a, b))"
    _maint__m_E_in_add((a, b))
    # End maint _m_E_in after "E.add((a, b))"
    # Begin maint _m_E_out after "E.add((a, b))"
    _maint__m_E_out_add((a, b))
    # End maint _m_E_out after "E.add((a, b))"
    # Begin maint Comp1_dE2 after "E.add((a, b))"
    _maint_Comp1_dE2_E_add((a, b))
    # End maint Comp1_dE2 after "E.add((a, b))"
    # Begin maint Comp1_Ty1 after "E.add((a, b))"
    _maint_Comp1_Ty1_E_add((a, b))
    # End maint Comp1_Ty1 after "E.add((a, b))"
    # Begin maint Comp1 after "E.add((a, b))"
    _maint_Comp1_E_add((a, b))
    # End maint Comp1 after "E.add((a, b))"
x = 1
print(sorted((_m_Comp1_out[x] if (x in _m_Comp1_out) else set())))