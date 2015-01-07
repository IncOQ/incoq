from invinc.runtime import *
# Comp1 := {x : (x, y) in E, f(y)}
# Comp4 := {(x, z) : (x, y) in E, (y, z) in E}
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

Comp4 = RCSet()
def _maint_Comp4_E_add(_e):
    v3_DAS = set()
    # Iterate {(v3_x, v3_y, v3_z) : (v3_x, v3_y) in deltamatch(E, 'bb', _e, 1), (v3_y, v3_z) in E}
    (v3_x, v3_y) = _e
    for v3_z in (_m_E_out[v3_y] if (v3_y in _m_E_out) else set()):
        if ((v3_x, v3_y, v3_z) not in v3_DAS):
            v3_DAS.add((v3_x, v3_y, v3_z))
    # Iterate {(v3_x, v3_y, v3_z) : (v3_x, v3_y) in E, (v3_y, v3_z) in deltamatch(E, 'bb', _e, 1)}
    (v3_y, v3_z) = _e
    for v3_x in (_m_E_in[v3_y] if (v3_y in _m_E_in) else set()):
        if ((v3_x, v3_y, v3_z) not in v3_DAS):
            v3_DAS.add((v3_x, v3_y, v3_z))
    for (v3_x, v3_y, v3_z) in v3_DAS:
        if ((v3_x, v3_z) not in Comp4):
            Comp4.add((v3_x, v3_z))
        else:
            Comp4.incref((v3_x, v3_z))
    del v3_DAS

Comp1 = RCSet()
def _maint_Comp1_E_add(_e):
    # Iterate {(v1_x, v1_y) : (v1_x, v1_y) in deltamatch(E, 'bb', _e, 1), f(v1_y)}
    (v1_x, v1_y) = _e
    if f(v1_y):
        if (v1_x not in Comp1):
            Comp1.add(v1_x)
        else:
            Comp1.incref(v1_x)

def f(y):
    return True

for (v1, v2) in {(1, 2), (1, 3), (2, 3), (3, 4)}:
    # Begin maint _m_E_in after "E.add((v1, v2))"
    _maint__m_E_in_add((v1, v2))
    # End maint _m_E_in after "E.add((v1, v2))"
    # Begin maint _m_E_out after "E.add((v1, v2))"
    _maint__m_E_out_add((v1, v2))
    # End maint _m_E_out after "E.add((v1, v2))"
    # Begin maint Comp4 after "E.add((v1, v2))"
    _maint_Comp4_E_add((v1, v2))
    # End maint Comp4 after "E.add((v1, v2))"
    # Begin maint Comp1 after "E.add((v1, v2))"
    _maint_Comp1_E_add((v1, v2))
    # End maint Comp1 after "E.add((v1, v2))"
print(sorted(Comp1))
print(sorted(Comp4))