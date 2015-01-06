from oinc.runtime import *
# Comp2 := {(y, (x, y)) : (x, y) in E}
_m_Comp2_out = Map()
def _maint__m_Comp2_out_add(_e):
    (v5_1, v5_2) = _e
    if (v5_1 not in _m_Comp2_out):
        _m_Comp2_out[v5_1] = set()
    _m_Comp2_out[v5_1].add(v5_2)

def _maint__m_Comp2_out_remove(_e):
    (v6_1, v6_2) = _e
    _m_Comp2_out[v6_1].remove(v6_2)
    if (len(_m_Comp2_out[v6_1]) == 0):
        del _m_Comp2_out[v6_1]

_m_E_out = Map()
def _maint__m_E_out_add(_e):
    (v3_1, v3_2) = _e
    if (v3_1 not in _m_E_out):
        _m_E_out[v3_1] = set()
    _m_E_out[v3_1].add(v3_2)

def _maint_Comp2_E_add(_e):
    # Iterate {(v1_x, v1_y) : (v1_x, v1_y) in deltamatch(E, 'bb', _e, 1)}
    (v1_x, v1_y) = _e
    # Begin maint _m_Comp2_out after "Comp2.add((v1_y, (v1_x, v1_y)))"
    _maint__m_Comp2_out_add((v1_y, (v1_x, v1_y)))
    # End maint _m_Comp2_out after "Comp2.add((v1_y, (v1_x, v1_y)))"

def query_Comp1(x):
    'x -> {y : (x, y) in E}'
    result = set()
    for y in (_m_E_out[x] if (x in _m_E_out) else set()):
        if (y not in result):
            result.add(y)
    return result

E = Set()
for (v1, v2) in {(1, 2), (2, 3), (2, 4), (4, 5)}:
    E.add((v1, v2))
    # Begin maint _m_E_out after "E.add((v1, v2))"
    _maint__m_E_out_add((v1, v2))
    # End maint _m_E_out after "E.add((v1, v2))"
    # Begin maint Comp2 after "E.add((v1, v2))"
    _maint_Comp2_E_add((v1, v2))
    # End maint Comp2 after "E.add((v1, v2))"
x = 1
y = 5
print(sorted({z for (x2, y) in E for (y2, z) in E if (x == x2) if (y == y2)}))
print(sorted(query_Comp1(x)))
print(sorted((_m_Comp2_out[y] if (y in _m_Comp2_out) else set())))