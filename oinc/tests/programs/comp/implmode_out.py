from oinc.runtime import *
# Comp2 := {(x, z) : (x, y) in E, (y, z) in E, (z > 3)}
# Comp3 := {(x, z) : (x, y) in E, (y, z) in E, (z > 4)}
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

Comp3 = RCSet()
def _maint_Comp3_E_add(_e):
    v3_DAS = set()
    # Iterate {(v3_x, v3_y, v3_z) : (v3_x, v3_y) in deltamatch(E, 'bb', _e, 1), (v3_y, v3_z) in E, (v3_z > 4)}
    (v3_x, v3_y) = _e
    for v3_z in (_m_E_out[v3_y] if (v3_y in _m_E_out) else set()):
        if (v3_z > 4):
            if ((v3_x, v3_y, v3_z) not in v3_DAS):
                v3_DAS.add((v3_x, v3_y, v3_z))
    # Iterate {(v3_x, v3_y, v3_z) : (v3_x, v3_y) in E, (v3_y, v3_z) in deltamatch(E, 'bb', _e, 1), (v3_z > 4)}
    (v3_y, v3_z) = _e
    if (v3_z > 4):
        for v3_x in (_m_E_in[v3_y] if (v3_y in _m_E_in) else set()):
            if ((v3_x, v3_y, v3_z) not in v3_DAS):
                v3_DAS.add((v3_x, v3_y, v3_z))
    for (v3_x, v3_y, v3_z) in v3_DAS:
        if ((v3_x, v3_z) not in Comp3):
            Comp3.add((v3_x, v3_z))
        else:
            Comp3.incref((v3_x, v3_z))
    del v3_DAS

Comp2 = RCSet()
def _maint_Comp2_E_add(_e):
    v1_DAS = set()
    for (v1_x, v1_y, v1_z) in {(v1_x, v1_y, v1_z) for (v1_x, v1_y) in {_e} for (v1_y_2, v1_z) in E if (v1_y == v1_y_2) if (v1_z > 3)}:
        if ((v1_x, v1_y, v1_z) not in v1_DAS):
            v1_DAS.add((v1_x, v1_y, v1_z))
    for (v1_x, v1_y, v1_z) in {(v1_x, v1_y, v1_z) for (v1_x, v1_y) in E for (v1_y_2, v1_z) in {_e} if (v1_y == v1_y_2) if (v1_z > 3)}:
        if ((v1_x, v1_y, v1_z) not in v1_DAS):
            v1_DAS.add((v1_x, v1_y, v1_z))
    for (v1_x, v1_y, v1_z) in v1_DAS:
        if ((v1_x, v1_z) not in Comp2):
            Comp2.add((v1_x, v1_z))
        else:
            Comp2.incref((v1_x, v1_z))
    del v1_DAS

def query_Comp1():
    '{(x, z) : (x, y) in E, (y, z) in E, (z > 2)}'
    result = set()
    for (x, y) in E:
        for z in (_m_E_out[y] if (y in _m_E_out) else set()):
            if (z > 2):
                if ((x, z) not in result):
                    result.add((x, z))
    return result

E = Set()
for (v1, v2) in {(1, 2), (2, 3), (3, 4), (4, 5)}:
    E.add((v1, v2))
    # Begin maint _m_E_in after "E.add((v1, v2))"
    _maint__m_E_in_add((v1, v2))
    # End maint _m_E_in after "E.add((v1, v2))"
    # Begin maint _m_E_out after "E.add((v1, v2))"
    _maint__m_E_out_add((v1, v2))
    # End maint _m_E_out after "E.add((v1, v2))"
    # Begin maint Comp3 after "E.add((v1, v2))"
    _maint_Comp3_E_add((v1, v2))
    # End maint Comp3 after "E.add((v1, v2))"
    # Begin maint Comp2 after "E.add((v1, v2))"
    _maint_Comp2_E_add((v1, v2))
    # End maint Comp2 after "E.add((v1, v2))"
print(sorted({(x, z) for (x, y) in E for (y2, z) in E if (y == y2) if (z > 1)}))
print(sorted(query_Comp1()))
print(sorted(Comp2))
print(sorted(Comp3))