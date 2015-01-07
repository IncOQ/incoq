from oinc.runtime import *
# Comp1 := {(a, a, c) : a in _U_Comp1, (a, b) in E, (b, c) in E}
# Comp8 := {(a, (x, z)) : a in _U_Comp8, (x, y) in E, (a, y, z) in Comp1}
# Comp8_Ta := {a : a in _U_Comp8}
# Comp1_delta := {a : a in Comp8_Ta}
_m_Comp8_out = Map()
def _maint__m_Comp8_out_add(_e):
    (v27_1, v27_2) = _e
    if (v27_1 not in _m_Comp8_out):
        _m_Comp8_out[v27_1] = set()
    _m_Comp8_out[v27_1].add(v27_2)

def _maint__m_Comp8_out_remove(_e):
    (v28_1, v28_2) = _e
    _m_Comp8_out[v28_1].remove(v28_2)
    if (len(_m_Comp8_out[v28_1]) == 0):
        del _m_Comp8_out[v28_1]

_m_E_out = Map()
def _maint__m_E_out_add(_e):
    (v25_1, v25_2) = _e
    if (v25_1 not in _m_E_out):
        _m_E_out[v25_1] = set()
    _m_E_out[v25_1].add(v25_2)

def _maint__m_E_out_remove(_e):
    (v26_1, v26_2) = _e
    _m_E_out[v26_1].remove(v26_2)
    if (len(_m_E_out[v26_1]) == 0):
        del _m_E_out[v26_1]

_m_Comp1_ubu = Map()
def _maint__m_Comp1_ubu_add(_e):
    (v23_1, v23_2, v23_3) = _e
    if (v23_2 not in _m_Comp1_ubu):
        _m_Comp1_ubu[v23_2] = set()
    _m_Comp1_ubu[v23_2].add((v23_1, v23_3))

def _maint__m_Comp1_ubu_remove(_e):
    (v24_1, v24_2, v24_3) = _e
    _m_Comp1_ubu[v24_2].remove((v24_1, v24_3))
    if (len(_m_Comp1_ubu[v24_2]) == 0):
        del _m_Comp1_ubu[v24_2]

_m_E_in = Map()
def _maint__m_E_in_add(_e):
    (v21_1, v21_2) = _e
    if (v21_2 not in _m_E_in):
        _m_E_in[v21_2] = set()
    _m_E_in[v21_2].add(v21_1)

def _maint__m_E_in_remove(_e):
    (v22_1, v22_2) = _e
    _m_E_in[v22_2].remove(v22_1)
    if (len(_m_E_in[v22_2]) == 0):
        del _m_E_in[v22_2]

_m_Comp1_buu = Map()
def _maint__m_Comp1_buu_add(_e):
    (v19_1, v19_2, v19_3) = _e
    if (v19_1 not in _m_Comp1_buu):
        _m_Comp1_buu[v19_1] = set()
    _m_Comp1_buu[v19_1].add((v19_2, v19_3))

def _maint__m_Comp1_buu_remove(_e):
    (v20_1, v20_2, v20_3) = _e
    _m_Comp1_buu[v20_1].remove((v20_2, v20_3))
    if (len(_m_Comp1_buu[v20_1]) == 0):
        del _m_Comp1_buu[v20_1]

Comp1_delta = RCSet()
def _maint_Comp1_delta_Comp8_Ta_add(_e):
    # Iterate {v13_a : v13_a in deltamatch(Comp8_Ta, 'b', _e, 1)}
    v13_a = _e
    Comp1_delta.add(v13_a)

def _maint_Comp8_Ta__U_Comp8_add(_e):
    # Iterate {v11_a : v11_a in deltamatch(_U_Comp8, 'b', _e, 1)}
    v11_a = _e
    # Begin maint Comp1_delta after "Comp8_Ta.add(v11_a)"
    _maint_Comp1_delta_Comp8_Ta_add(v11_a)
    # End maint Comp1_delta after "Comp8_Ta.add(v11_a)"

def _maint_Comp8_Ta__U_Comp8_remove(_e):
    # Iterate {v12_a : v12_a in deltamatch(_U_Comp8, 'b', _e, 1)}
    v12_a = _e
    # Begin maint Comp1_delta before "Comp8_Ta.remove(v12_a)"
    _maint_Comp1_delta_Comp8_Ta_add(v12_a)
    # End maint Comp1_delta before "Comp8_Ta.remove(v12_a)"

Comp8 = RCSet()
def _maint_Comp8__U_Comp8_add(_e):
    # Iterate {(v5_a, v5_x, v5_y, v5_z) : v5_a in deltamatch(_U_Comp8, 'b', _e, 1), (v5_x, v5_y) in E, (v5_a, v5_y, v5_z) in Comp1}
    v5_a = _e
    for (v5_y, v5_z) in (_m_Comp1_buu[v5_a] if (v5_a in _m_Comp1_buu) else set()):
        for v5_x in (_m_E_in[v5_y] if (v5_y in _m_E_in) else set()):
            if ((v5_a, (v5_x, v5_z)) not in Comp8):
                Comp8.add((v5_a, (v5_x, v5_z)))
                # Begin maint _m_Comp8_out after "Comp8.add((v5_a, (v5_x, v5_z)))"
                _maint__m_Comp8_out_add((v5_a, (v5_x, v5_z)))
                # End maint _m_Comp8_out after "Comp8.add((v5_a, (v5_x, v5_z)))"
            else:
                Comp8.incref((v5_a, (v5_x, v5_z)))

def _maint_Comp8__U_Comp8_remove(_e):
    # Iterate {(v6_a, v6_x, v6_y, v6_z) : v6_a in deltamatch(_U_Comp8, 'b', _e, 1), (v6_x, v6_y) in E, (v6_a, v6_y, v6_z) in Comp1}
    v6_a = _e
    for (v6_y, v6_z) in (_m_Comp1_buu[v6_a] if (v6_a in _m_Comp1_buu) else set()):
        for v6_x in (_m_E_in[v6_y] if (v6_y in _m_E_in) else set()):
            if (Comp8.getref((v6_a, (v6_x, v6_z))) == 1):
                # Begin maint _m_Comp8_out before "Comp8.remove((v6_a, (v6_x, v6_z)))"
                _maint__m_Comp8_out_remove((v6_a, (v6_x, v6_z)))
                # End maint _m_Comp8_out before "Comp8.remove((v6_a, (v6_x, v6_z)))"
                Comp8.remove((v6_a, (v6_x, v6_z)))
            else:
                Comp8.decref((v6_a, (v6_x, v6_z)))

def _maint_Comp8_E_add(_e):
    # Iterate {(v7_a, v7_x, v7_y, v7_z) : v7_a in _U_Comp8, (v7_x, v7_y) in deltamatch(E, 'bb', _e, 1), (v7_a, v7_y, v7_z) in Comp1}
    (v7_x, v7_y) = _e
    for (v7_a, v7_z) in (_m_Comp1_ubu[v7_y] if (v7_y in _m_Comp1_ubu) else set()):
        if (v7_a in _U_Comp8):
            if ((v7_a, (v7_x, v7_z)) not in Comp8):
                Comp8.add((v7_a, (v7_x, v7_z)))
                # Begin maint _m_Comp8_out after "Comp8.add((v7_a, (v7_x, v7_z)))"
                _maint__m_Comp8_out_add((v7_a, (v7_x, v7_z)))
                # End maint _m_Comp8_out after "Comp8.add((v7_a, (v7_x, v7_z)))"
            else:
                Comp8.incref((v7_a, (v7_x, v7_z)))

def _maint_Comp8_E_remove(_e):
    # Iterate {(v8_a, v8_x, v8_y, v8_z) : v8_a in _U_Comp8, (v8_x, v8_y) in deltamatch(E, 'bb', _e, 1), (v8_a, v8_y, v8_z) in Comp1}
    (v8_x, v8_y) = _e
    for (v8_a, v8_z) in (_m_Comp1_ubu[v8_y] if (v8_y in _m_Comp1_ubu) else set()):
        if (v8_a in _U_Comp8):
            if (Comp8.getref((v8_a, (v8_x, v8_z))) == 1):
                # Begin maint _m_Comp8_out before "Comp8.remove((v8_a, (v8_x, v8_z)))"
                _maint__m_Comp8_out_remove((v8_a, (v8_x, v8_z)))
                # End maint _m_Comp8_out before "Comp8.remove((v8_a, (v8_x, v8_z)))"
                Comp8.remove((v8_a, (v8_x, v8_z)))
            else:
                Comp8.decref((v8_a, (v8_x, v8_z)))

def _maint_Comp8_Comp1_add(_e):
    # Iterate {(v9_a, v9_x, v9_y, v9_z) : v9_a in _U_Comp8, (v9_x, v9_y) in E, (v9_a, v9_y, v9_z) in deltamatch(Comp1, 'bbb', _e, 1)}
    (v9_a, v9_y, v9_z) = _e
    if (v9_a in _U_Comp8):
        for v9_x in (_m_E_in[v9_y] if (v9_y in _m_E_in) else set()):
            if ((v9_a, (v9_x, v9_z)) not in Comp8):
                Comp8.add((v9_a, (v9_x, v9_z)))
                # Begin maint _m_Comp8_out after "Comp8.add((v9_a, (v9_x, v9_z)))"
                _maint__m_Comp8_out_add((v9_a, (v9_x, v9_z)))
                # End maint _m_Comp8_out after "Comp8.add((v9_a, (v9_x, v9_z)))"
            else:
                Comp8.incref((v9_a, (v9_x, v9_z)))

def _maint_Comp8_Comp1_remove(_e):
    # Iterate {(v10_a, v10_x, v10_y, v10_z) : v10_a in _U_Comp8, (v10_x, v10_y) in E, (v10_a, v10_y, v10_z) in deltamatch(Comp1, 'bbb', _e, 1)}
    (v10_a, v10_y, v10_z) = _e
    if (v10_a in _U_Comp8):
        for v10_x in (_m_E_in[v10_y] if (v10_y in _m_E_in) else set()):
            if (Comp8.getref((v10_a, (v10_x, v10_z))) == 1):
                # Begin maint _m_Comp8_out before "Comp8.remove((v10_a, (v10_x, v10_z)))"
                _maint__m_Comp8_out_remove((v10_a, (v10_x, v10_z)))
                # End maint _m_Comp8_out before "Comp8.remove((v10_a, (v10_x, v10_z)))"
                Comp8.remove((v10_a, (v10_x, v10_z)))
            else:
                Comp8.decref((v10_a, (v10_x, v10_z)))

_U_Comp8 = RCSet()
_UEXT_Comp8 = Set()
def demand_Comp8(a):
    '{(a, (x, z)) : a in _U_Comp8, (x, y) in E, (a, y, z) in Comp1}'
    if (a not in _U_Comp8):
        _U_Comp8.add(a)
        # Begin maint Comp8_Ta after "_U_Comp8.add(a)"
        _maint_Comp8_Ta__U_Comp8_add(a)
        # End maint Comp8_Ta after "_U_Comp8.add(a)"
        # Begin maint Comp8 after "_U_Comp8.add(a)"
        _maint_Comp8__U_Comp8_add(a)
        # End maint Comp8 after "_U_Comp8.add(a)"
        # Begin maint demand_Comp1 after "_U_Comp8.add(a)"
        for v15_a in Comp1_delta.elements():
            demand_Comp1(v15_a)
        Comp1_delta.clear()
        # End maint demand_Comp1 after "_U_Comp8.add(a)"
    else:
        _U_Comp8.incref(a)

def undemand_Comp8(a):
    '{(a, (x, z)) : a in _U_Comp8, (x, y) in E, (a, y, z) in Comp1}'
    if (_U_Comp8.getref(a) == 1):
        # Begin maint Comp8 before "_U_Comp8.remove(a)"
        _maint_Comp8__U_Comp8_remove(a)
        # End maint Comp8 before "_U_Comp8.remove(a)"
        # Begin maint Comp8_Ta before "_U_Comp8.remove(a)"
        _maint_Comp8_Ta__U_Comp8_remove(a)
        # End maint Comp8_Ta before "_U_Comp8.remove(a)"
        _U_Comp8.remove(a)
        # Begin maint undemand_Comp1 after "_U_Comp8.remove(a)"
        for v16_a in Comp1_delta.elements():
            undemand_Comp1(v16_a)
        Comp1_delta.clear()
        # End maint undemand_Comp1 after "_U_Comp8.remove(a)"
    else:
        _U_Comp8.decref(a)

def query_Comp8(a):
    '{(a, (x, z)) : a in _U_Comp8, (x, y) in E, (a, y, z) in Comp1}'
    if (a not in _UEXT_Comp8):
        _UEXT_Comp8.add(a)
        demand_Comp8(a)
    return True

Comp1 = RCSet()
def _maint_Comp1__U_Comp1_add(_e):
    # Iterate {(v1_a, v1_b, v1_c) : v1_a in deltamatch(_U_Comp1, 'b', _e, 1), (v1_a, v1_b) in E, (v1_b, v1_c) in E}
    v1_a = _e
    for v1_b in (_m_E_out[v1_a] if (v1_a in _m_E_out) else set()):
        for v1_c in (_m_E_out[v1_b] if (v1_b in _m_E_out) else set()):
            if ((v1_a, v1_a, v1_c) not in Comp1):
                Comp1.add((v1_a, v1_a, v1_c))
                # Begin maint _m_Comp1_ubu after "Comp1.add((v1_a, v1_a, v1_c))"
                _maint__m_Comp1_ubu_add((v1_a, v1_a, v1_c))
                # End maint _m_Comp1_ubu after "Comp1.add((v1_a, v1_a, v1_c))"
                # Begin maint _m_Comp1_buu after "Comp1.add((v1_a, v1_a, v1_c))"
                _maint__m_Comp1_buu_add((v1_a, v1_a, v1_c))
                # End maint _m_Comp1_buu after "Comp1.add((v1_a, v1_a, v1_c))"
                # Begin maint Comp8 after "Comp1.add((v1_a, v1_a, v1_c))"
                _maint_Comp8_Comp1_add((v1_a, v1_a, v1_c))
                # End maint Comp8 after "Comp1.add((v1_a, v1_a, v1_c))"
            else:
                Comp1.incref((v1_a, v1_a, v1_c))

def _maint_Comp1__U_Comp1_remove(_e):
    # Iterate {(v2_a, v2_b, v2_c) : v2_a in deltamatch(_U_Comp1, 'b', _e, 1), (v2_a, v2_b) in E, (v2_b, v2_c) in E}
    v2_a = _e
    for v2_b in (_m_E_out[v2_a] if (v2_a in _m_E_out) else set()):
        for v2_c in (_m_E_out[v2_b] if (v2_b in _m_E_out) else set()):
            if (Comp1.getref((v2_a, v2_a, v2_c)) == 1):
                # Begin maint Comp8 before "Comp1.remove((v2_a, v2_a, v2_c))"
                _maint_Comp8_Comp1_remove((v2_a, v2_a, v2_c))
                # End maint Comp8 before "Comp1.remove((v2_a, v2_a, v2_c))"
                # Begin maint _m_Comp1_buu before "Comp1.remove((v2_a, v2_a, v2_c))"
                _maint__m_Comp1_buu_remove((v2_a, v2_a, v2_c))
                # End maint _m_Comp1_buu before "Comp1.remove((v2_a, v2_a, v2_c))"
                # Begin maint _m_Comp1_ubu before "Comp1.remove((v2_a, v2_a, v2_c))"
                _maint__m_Comp1_ubu_remove((v2_a, v2_a, v2_c))
                # End maint _m_Comp1_ubu before "Comp1.remove((v2_a, v2_a, v2_c))"
                Comp1.remove((v2_a, v2_a, v2_c))
            else:
                Comp1.decref((v2_a, v2_a, v2_c))

def _maint_Comp1_E_add(_e):
    v3_DAS = set()
    # Iterate {(v3_a, v3_b, v3_c) : v3_a in _U_Comp1, (v3_a, v3_b) in deltamatch(E, 'bb', _e, 1), (v3_b, v3_c) in E}
    (v3_a, v3_b) = _e
    if (v3_a in _U_Comp1):
        for v3_c in (_m_E_out[v3_b] if (v3_b in _m_E_out) else set()):
            if ((v3_a, v3_b, v3_c) not in v3_DAS):
                v3_DAS.add((v3_a, v3_b, v3_c))
    # Iterate {(v3_a, v3_b, v3_c) : v3_a in _U_Comp1, (v3_a, v3_b) in E, (v3_b, v3_c) in deltamatch(E, 'bb', _e, 1)}
    (v3_b, v3_c) = _e
    for v3_a in (_m_E_in[v3_b] if (v3_b in _m_E_in) else set()):
        if (v3_a in _U_Comp1):
            if ((v3_a, v3_b, v3_c) not in v3_DAS):
                v3_DAS.add((v3_a, v3_b, v3_c))
    for (v3_a, v3_b, v3_c) in v3_DAS:
        if ((v3_a, v3_a, v3_c) not in Comp1):
            Comp1.add((v3_a, v3_a, v3_c))
            # Begin maint _m_Comp1_ubu after "Comp1.add((v3_a, v3_a, v3_c))"
            _maint__m_Comp1_ubu_add((v3_a, v3_a, v3_c))
            # End maint _m_Comp1_ubu after "Comp1.add((v3_a, v3_a, v3_c))"
            # Begin maint _m_Comp1_buu after "Comp1.add((v3_a, v3_a, v3_c))"
            _maint__m_Comp1_buu_add((v3_a, v3_a, v3_c))
            # End maint _m_Comp1_buu after "Comp1.add((v3_a, v3_a, v3_c))"
            # Begin maint Comp8 after "Comp1.add((v3_a, v3_a, v3_c))"
            _maint_Comp8_Comp1_add((v3_a, v3_a, v3_c))
            # End maint Comp8 after "Comp1.add((v3_a, v3_a, v3_c))"
        else:
            Comp1.incref((v3_a, v3_a, v3_c))
    del v3_DAS

def _maint_Comp1_E_remove(_e):
    v4_DAS = set()
    # Iterate {(v4_a, v4_b, v4_c) : v4_a in _U_Comp1, (v4_a, v4_b) in deltamatch(E, 'bb', _e, 1), (v4_b, v4_c) in E}
    (v4_a, v4_b) = _e
    if (v4_a in _U_Comp1):
        for v4_c in (_m_E_out[v4_b] if (v4_b in _m_E_out) else set()):
            if ((v4_a, v4_b, v4_c) not in v4_DAS):
                v4_DAS.add((v4_a, v4_b, v4_c))
    # Iterate {(v4_a, v4_b, v4_c) : v4_a in _U_Comp1, (v4_a, v4_b) in E, (v4_b, v4_c) in deltamatch(E, 'bb', _e, 1)}
    (v4_b, v4_c) = _e
    for v4_a in (_m_E_in[v4_b] if (v4_b in _m_E_in) else set()):
        if (v4_a in _U_Comp1):
            if ((v4_a, v4_b, v4_c) not in v4_DAS):
                v4_DAS.add((v4_a, v4_b, v4_c))
    for (v4_a, v4_b, v4_c) in v4_DAS:
        if (Comp1.getref((v4_a, v4_a, v4_c)) == 1):
            # Begin maint Comp8 before "Comp1.remove((v4_a, v4_a, v4_c))"
            _maint_Comp8_Comp1_remove((v4_a, v4_a, v4_c))
            # End maint Comp8 before "Comp1.remove((v4_a, v4_a, v4_c))"
            # Begin maint _m_Comp1_buu before "Comp1.remove((v4_a, v4_a, v4_c))"
            _maint__m_Comp1_buu_remove((v4_a, v4_a, v4_c))
            # End maint _m_Comp1_buu before "Comp1.remove((v4_a, v4_a, v4_c))"
            # Begin maint _m_Comp1_ubu before "Comp1.remove((v4_a, v4_a, v4_c))"
            _maint__m_Comp1_ubu_remove((v4_a, v4_a, v4_c))
            # End maint _m_Comp1_ubu before "Comp1.remove((v4_a, v4_a, v4_c))"
            Comp1.remove((v4_a, v4_a, v4_c))
        else:
            Comp1.decref((v4_a, v4_a, v4_c))
    del v4_DAS

_U_Comp1 = RCSet()
_UEXT_Comp1 = Set()
def demand_Comp1(a):
    '{(a, a, c) : a in _U_Comp1, (a, b) in E, (b, c) in E}'
    if (a not in _U_Comp1):
        _U_Comp1.add(a)
        # Begin maint Comp1 after "_U_Comp1.add(a)"
        _maint_Comp1__U_Comp1_add(a)
        # End maint Comp1 after "_U_Comp1.add(a)"
    else:
        _U_Comp1.incref(a)

def undemand_Comp1(a):
    '{(a, a, c) : a in _U_Comp1, (a, b) in E, (b, c) in E}'
    if (_U_Comp1.getref(a) == 1):
        # Begin maint Comp1 before "_U_Comp1.remove(a)"
        _maint_Comp1__U_Comp1_remove(a)
        # End maint Comp1 before "_U_Comp1.remove(a)"
        _U_Comp1.remove(a)
    else:
        _U_Comp1.decref(a)

def query_Comp1(a):
    '{(a, a, c) : a in _U_Comp1, (a, b) in E, (b, c) in E}'
    if (a not in _UEXT_Comp1):
        _UEXT_Comp1.add(a)
        demand_Comp1(a)
    return True

for (v1, v2) in [(1, 2), (2, 3), (3, 4), (4, 5)]:
    # Begin maint _m_E_out after "E.add((v1, v2))"
    _maint__m_E_out_add((v1, v2))
    # End maint _m_E_out after "E.add((v1, v2))"
    # Begin maint _m_E_in after "E.add((v1, v2))"
    _maint__m_E_in_add((v1, v2))
    # End maint _m_E_in after "E.add((v1, v2))"
    # Begin maint Comp8 after "E.add((v1, v2))"
    _maint_Comp8_E_add((v1, v2))
    # End maint Comp8 after "E.add((v1, v2))"
    # Begin maint Comp1 after "E.add((v1, v2))"
    _maint_Comp1_E_add((v1, v2))
    # End maint Comp1 after "E.add((v1, v2))"
    # Begin maint demand_Comp1 after "E.add((v1, v2))"
    for v17_a in Comp1_delta.elements():
        demand_Comp1(v17_a)
    Comp1_delta.clear()
    # End maint demand_Comp1 after "E.add((v1, v2))"
def query(a):
    print(sorted((query_Comp8(a) and (_m_Comp8_out[a] if (a in _m_Comp8_out) else set()))))

query(2)
# Begin maint Comp1 before "E.remove((1, 2))"
_maint_Comp1_E_remove((1, 2))
# End maint Comp1 before "E.remove((1, 2))"
# Begin maint Comp8 before "E.remove((1, 2))"
_maint_Comp8_E_remove((1, 2))
# End maint Comp8 before "E.remove((1, 2))"
# Begin maint _m_E_in before "E.remove((1, 2))"
_maint__m_E_in_remove((1, 2))
# End maint _m_E_in before "E.remove((1, 2))"
# Begin maint _m_E_out before "E.remove((1, 2))"
_maint__m_E_out_remove((1, 2))
# End maint _m_E_out before "E.remove((1, 2))"
# Begin maint undemand_Comp1 after "E.remove((1, 2))"
for v18_a in Comp1_delta.elements():
    undemand_Comp1(v18_a)
Comp1_delta.clear()
# End maint undemand_Comp1 after "E.remove((1, 2))"
query(2)