from invinc.runtime import *
# Comp1 := {z : (x, x) in E, (x, y) in E, (y, z) in S}
_m_E_u1 = Map()
def _maint__m_E_u1_add(_e):
    (v11_1, v11_2) = _e
    if ((v11_1 == v11_2)):
        if (() not in _m_E_u1):
            _m_E_u1[()] = set()
        _m_E_u1[()].add(v11_1)

_m_E_b1 = Map()
def _maint__m_E_b1_add(_e):
    (v9_1, v9_2) = _e
    if ((v9_1 == v9_2)):
        if (v9_1 not in _m_E_b1):
            _m_E_b1[v9_1] = set()
        _m_E_b1[v9_1].add(())

_m_S_out = Map()
def _maint__m_S_out_add(_e):
    (v7_1, v7_2) = _e
    if (v7_1 not in _m_S_out):
        _m_S_out[v7_1] = set()
    _m_S_out[v7_1].add(v7_2)

def _maint__m_S_out_remove(_e):
    (v8_1, v8_2) = _e
    _m_S_out[v8_1].remove(v8_2)
    if (len(_m_S_out[v8_1]) == 0):
        del _m_S_out[v8_1]

_m_E_out = Map()
def _maint__m_E_out_add(_e):
    (v5_1, v5_2) = _e
    if (v5_1 not in _m_E_out):
        _m_E_out[v5_1] = set()
    _m_E_out[v5_1].add(v5_2)

Comp1 = RCSet()
def _maint_Comp1_E_add(_e):
    # Iterate {(v1_x, v1_y, v1_z) : (v1_x, v1_x) in deltamatch(E, 'b1', _e, 1), (v1_x, v1_y) in (E - {_e}), (v1_y, v1_z) in S}
    for v1_x in setmatch({_e}, 'u1', ()):
        for v1_y in (_m_E_out[v1_x] if (v1_x in _m_E_out) else set()):
            if ((v1_x, v1_y) != _e):
                for v1_z in (_m_S_out[v1_y] if (v1_y in _m_S_out) else set()):
                    if (v1_z not in Comp1):
                        Comp1.add(v1_z)
                    else:
                        Comp1.incref(v1_z)
    # Iterate {(v1_x, v1_y, v1_z) : (v1_x, v1_x) in E, (v1_x, v1_y) in deltamatch(E, 'bb', _e, 1), (v1_y, v1_z) in S}
    (v1_x, v1_y) = _e
    for _ in (_m_E_b1[v1_x] if (v1_x in _m_E_b1) else set()):
        for v1_z in (_m_S_out[v1_y] if (v1_y in _m_S_out) else set()):
            if (v1_z not in Comp1):
                Comp1.add(v1_z)
            else:
                Comp1.incref(v1_z)

def _maint_Comp1_S_add(_e):
    # Iterate {(v3_x, v3_y, v3_z) : (v3_x, v3_x) in E, (v3_x, v3_y) in E, (v3_y, v3_z) in deltamatch(S, 'bb', _e, 1)}
    (v3_y, v3_z) = _e
    for v3_x in (_m_E_u1[()] if (() in _m_E_u1) else set()):
        if ((v3_x, v3_y) in E):
            if (v3_z not in Comp1):
                Comp1.add(v3_z)
            else:
                Comp1.incref(v3_z)

def _maint_Comp1_S_remove(_e):
    # Iterate {(v4_x, v4_y, v4_z) : (v4_x, v4_x) in E, (v4_x, v4_y) in E, (v4_y, v4_z) in deltamatch(S, 'bb', _e, 1)}
    (v4_y, v4_z) = _e
    for v4_x in (_m_E_u1[()] if (() in _m_E_u1) else set()):
        if ((v4_x, v4_y) in E):
            if (Comp1.getref(v4_z) == 1):
                Comp1.remove(v4_z)
            else:
                Comp1.decref(v4_z)

E = Set()
# Begin maint _m_S_out after "S.add((1, 2))"
_maint__m_S_out_add((1, 2))
# End maint _m_S_out after "S.add((1, 2))"
# Begin maint Comp1 after "S.add((1, 2))"
_maint_Comp1_S_add((1, 2))
# End maint Comp1 after "S.add((1, 2))"
E.add((1, 1))
# Begin maint _m_E_u1 after "E.add((1, 1))"
_maint__m_E_u1_add((1, 1))
# End maint _m_E_u1 after "E.add((1, 1))"
# Begin maint _m_E_b1 after "E.add((1, 1))"
_maint__m_E_b1_add((1, 1))
# End maint _m_E_b1 after "E.add((1, 1))"
# Begin maint _m_E_out after "E.add((1, 1))"
_maint__m_E_out_add((1, 1))
# End maint _m_E_out after "E.add((1, 1))"
# Begin maint Comp1 after "E.add((1, 1))"
_maint_Comp1_E_add((1, 1))
# End maint Comp1 after "E.add((1, 1))"
# Begin maint Comp1 before "S.remove((1, 2))"
_maint_Comp1_S_remove((1, 2))
# End maint Comp1 before "S.remove((1, 2))"
# Begin maint _m_S_out before "S.remove((1, 2))"
_maint__m_S_out_remove((1, 2))
# End maint _m_S_out before "S.remove((1, 2))"
print(sorted(Comp1))