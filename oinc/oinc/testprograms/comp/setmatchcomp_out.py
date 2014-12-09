from runtimelib import *
# Comp1 := {(x, z) : (x, y) in E, (y, z) in E}
_m_Comp1_out = Map()
def _maint__m_Comp1_out_add(_e):
    (v7_1, v7_2) = _e
    if (v7_1 not in _m_Comp1_out):
        _m_Comp1_out[v7_1] = set()
    _m_Comp1_out[v7_1].add(v7_2)

def _maint__m_Comp1_out_remove(_e):
    (v8_1, v8_2) = _e
    _m_Comp1_out[v8_1].remove(v8_2)
    if (len(_m_Comp1_out[v8_1]) == 0):
        del _m_Comp1_out[v8_1]

_m_E_in = Map()
def _maint__m_E_in_add(_e):
    (v5_1, v5_2) = _e
    if (v5_2 not in _m_E_in):
        _m_E_in[v5_2] = set()
    _m_E_in[v5_2].add(v5_1)

_m_E_out = Map()
def _maint__m_E_out_add(_e):
    (v3_1, v3_2) = _e
    if (v3_1 not in _m_E_out):
        _m_E_out[v3_1] = set()
    _m_E_out[v3_1].add(v3_2)

Comp1 = RCSet()
def _maint_Comp1_E_add(_e):
    v1_DAS = set()
    # Iterate {(v1_x, v1_y, v1_z) : (v1_x, v1_y) in deltamatch(E, 'bb', _e, 1), (v1_y, v1_z) in E}
    (v1_x, v1_y) = _e
    for v1_z in (_m_E_out[v1_y] if (v1_y in _m_E_out) else set()):
        if ((v1_x, v1_y, v1_z) not in v1_DAS):
            v1_DAS.add((v1_x, v1_y, v1_z))
    # Iterate {(v1_x, v1_y, v1_z) : (v1_x, v1_y) in E, (v1_y, v1_z) in deltamatch(E, 'bb', _e, 1)}
    (v1_y, v1_z) = _e
    for v1_x in (_m_E_in[v1_y] if (v1_y in _m_E_in) else set()):
        if ((v1_x, v1_y, v1_z) not in v1_DAS):
            v1_DAS.add((v1_x, v1_y, v1_z))
    for (v1_x, v1_y, v1_z) in v1_DAS:
        if ((v1_x, v1_z) not in Comp1):
            Comp1.add((v1_x, v1_z))
            # Begin maint _m_Comp1_out after "Comp1.add((v1_x, v1_z))"
            _maint__m_Comp1_out_add((v1_x, v1_z))
            # End maint _m_Comp1_out after "Comp1.add((v1_x, v1_z))"
        else:
            Comp1.incref((v1_x, v1_z))
    del v1_DAS

for (v1, v2) in {(1, 2), (1, 3), (2, 3), (3, 4)}:
    # Begin maint _m_E_in after "E.add((v1, v2))"
    _maint__m_E_in_add((v1, v2))
    # End maint _m_E_in after "E.add((v1, v2))"
    # Begin maint _m_E_out after "E.add((v1, v2))"
    _maint__m_E_out_add((v1, v2))
    # End maint _m_E_out after "E.add((v1, v2))"
    # Begin maint Comp1 after "E.add((v1, v2))"
    _maint_Comp1_E_add((v1, v2))
    # End maint Comp1 after "E.add((v1, v2))"
p = 1
print(sorted((_m_Comp1_out[p] if (p in _m_Comp1_out) else set())))