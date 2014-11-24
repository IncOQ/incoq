from runtimelib import *
# Comp1 := {z : _ in _U_Comp1, (x, x) in E, (x, y) in E, (y, z) in S}
# Comp1_Tx1 := {x : (x, x) in E}
# Comp1_dE2 := {(x, y) : x in Comp1_Tx1, (x, y) in E}
# Comp1_Ty1 := {y : (x, y) in Comp1_dE2}
# Comp1_dS := {(y, z) : y in Comp1_Ty1, (y, z) in S}
_m_E_b1 = Map()
def _maint__m_E_b1_add(_e):
    (v31_1, v31_2) = _e
    if ((v31_1 == v31_2)):
        if (v31_1 not in _m_E_b1):
            _m_E_b1[v31_1] = set()
        _m_E_b1[v31_1].add(())

_m_Comp1_dS_out = Map()
def _maint__m_Comp1_dS_out_add(_e):
    (v29_1, v29_2) = _e
    if (v29_1 not in _m_Comp1_dS_out):
        _m_Comp1_dS_out[v29_1] = set()
    _m_Comp1_dS_out[v29_1].add(v29_2)

def _maint__m_Comp1_dS_out_remove(_e):
    (v30_1, v30_2) = _e
    _m_Comp1_dS_out[v30_1].remove(v30_2)
    if (len(_m_Comp1_dS_out[v30_1]) == 0):
        del _m_Comp1_dS_out[v30_1]

_m_Comp1_dE2_out = Map()
def _maint__m_Comp1_dE2_out_add(_e):
    (v27_1, v27_2) = _e
    if (v27_1 not in _m_Comp1_dE2_out):
        _m_Comp1_dE2_out[v27_1] = set()
    _m_Comp1_dE2_out[v27_1].add(v27_2)

def _maint__m_Comp1_dE2_out_remove(_e):
    (v28_1, v28_2) = _e
    _m_Comp1_dE2_out[v28_1].remove(v28_2)
    if (len(_m_Comp1_dE2_out[v28_1]) == 0):
        del _m_Comp1_dE2_out[v28_1]

_m_E_u1 = Map()
def _maint__m_E_u1_add(_e):
    (v25_1, v25_2) = _e
    if ((v25_1 == v25_2)):
        if (() not in _m_E_u1):
            _m_E_u1[()] = set()
        _m_E_u1[()].add(v25_1)

_m__U_Comp1_w = Map()
def _maint__m__U_Comp1_w_add(_e):
    if (() not in _m__U_Comp1_w):
        _m__U_Comp1_w[()] = RCSet()
    if (() not in _m__U_Comp1_w[()]):
        _m__U_Comp1_w[()].add(())
    else:
        _m__U_Comp1_w[()].incref(())

def _maint__m__U_Comp1_w_remove(_e):
    if (_m__U_Comp1_w[()].getref(()) == 1):
        _m__U_Comp1_w[()].remove(())
    else:
        _m__U_Comp1_w[()].decref(())
    if (len(_m__U_Comp1_w[()]) == 0):
        del _m__U_Comp1_w[()]

_m_E_out = Map()
def _maint__m_E_out_add(_e):
    (v21_1, v21_2) = _e
    if (v21_1 not in _m_E_out):
        _m_E_out[v21_1] = set()
    _m_E_out[v21_1].add(v21_2)

_m_S_out = Map()
def _maint__m_S_out_add(_e):
    (v19_1, v19_2) = _e
    if (v19_1 not in _m_S_out):
        _m_S_out[v19_1] = set()
    _m_S_out[v19_1].add(v19_2)

def _maint__m_S_out_remove(_e):
    (v20_1, v20_2) = _e
    _m_S_out[v20_1].remove(v20_2)
    if (len(_m_S_out[v20_1]) == 0):
        del _m_S_out[v20_1]

Comp1_dS = RCSet()
def _maint_Comp1_dS_Comp1_Ty1_add(_e):
    # Iterate {(v15_y, v15_z) : v15_y in deltamatch(Comp1_Ty1, 'b', _e, 0), (v15_y, v15_z) in S}
    v15_y = _e
    for v15_z in (_m_S_out[v15_y] if (v15_y in _m_S_out) else set()):
        Comp1_dS.add((v15_y, v15_z))
        # Begin maint _m_Comp1_dS_out after "Comp1_dS.add((v15_y, v15_z))"
        _maint__m_Comp1_dS_out_add((v15_y, v15_z))
        # End maint _m_Comp1_dS_out after "Comp1_dS.add((v15_y, v15_z))"

def _maint_Comp1_dS_Comp1_Ty1_remove(_e):
    # Iterate {(v16_y, v16_z) : v16_y in deltamatch(Comp1_Ty1, 'b', _e, 0), (v16_y, v16_z) in S}
    v16_y = _e
    for v16_z in (_m_S_out[v16_y] if (v16_y in _m_S_out) else set()):
        # Begin maint _m_Comp1_dS_out before "Comp1_dS.remove((v16_y, v16_z))"
        _maint__m_Comp1_dS_out_remove((v16_y, v16_z))
        # End maint _m_Comp1_dS_out before "Comp1_dS.remove((v16_y, v16_z))"
        Comp1_dS.remove((v16_y, v16_z))

def _maint_Comp1_dS_S_add(_e):
    # Iterate {(v17_y, v17_z) : v17_y in Comp1_Ty1, (v17_y, v17_z) in deltamatch(S, 'bb', _e, 0)}
    (v17_y, v17_z) = _e
    if (v17_y in Comp1_Ty1):
        Comp1_dS.add((v17_y, v17_z))
        # Begin maint _m_Comp1_dS_out after "Comp1_dS.add((v17_y, v17_z))"
        _maint__m_Comp1_dS_out_add((v17_y, v17_z))
        # End maint _m_Comp1_dS_out after "Comp1_dS.add((v17_y, v17_z))"

def _maint_Comp1_dS_S_remove(_e):
    # Iterate {(v18_y, v18_z) : v18_y in Comp1_Ty1, (v18_y, v18_z) in deltamatch(S, 'bb', _e, 0)}
    (v18_y, v18_z) = _e
    if (v18_y in Comp1_Ty1):
        # Begin maint _m_Comp1_dS_out before "Comp1_dS.remove((v18_y, v18_z))"
        _maint__m_Comp1_dS_out_remove((v18_y, v18_z))
        # End maint _m_Comp1_dS_out before "Comp1_dS.remove((v18_y, v18_z))"
        Comp1_dS.remove((v18_y, v18_z))

Comp1_Ty1 = RCSet()
def _maint_Comp1_Ty1_Comp1_dE2_add(_e):
    # Iterate {(v13_x, v13_y) : (v13_x, v13_y) in deltamatch(Comp1_dE2, 'bb', _e, 0)}
    (v13_x, v13_y) = _e
    if (v13_y not in Comp1_Ty1):
        # Begin maint Comp1_dS before "Comp1_Ty1.add(v13_y)"
        _maint_Comp1_dS_Comp1_Ty1_add(v13_y)
        # End maint Comp1_dS before "Comp1_Ty1.add(v13_y)"
        Comp1_Ty1.add(v13_y)
    else:
        Comp1_Ty1.incref(v13_y)

def _maint_Comp1_Ty1_Comp1_dE2_remove(_e):
    # Iterate {(v14_x, v14_y) : (v14_x, v14_y) in deltamatch(Comp1_dE2, 'bb', _e, 0)}
    (v14_x, v14_y) = _e
    if (Comp1_Ty1.getref(v14_y) == 1):
        Comp1_Ty1.remove(v14_y)
        # Begin maint Comp1_dS after "Comp1_Ty1.remove(v14_y)"
        _maint_Comp1_dS_Comp1_Ty1_remove(v14_y)
        # End maint Comp1_dS after "Comp1_Ty1.remove(v14_y)"
    else:
        Comp1_Ty1.decref(v14_y)

Comp1_dE2 = RCSet()
def _maint_Comp1_dE2_Comp1_Tx1_add(_e):
    # Iterate {(v9_x, v9_y) : v9_x in deltamatch(Comp1_Tx1, 'b', _e, 0), (v9_x, v9_y) in E}
    v9_x = _e
    for v9_y in (_m_E_out[v9_x] if (v9_x in _m_E_out) else set()):
        # Begin maint Comp1_Ty1 before "Comp1_dE2.add((v9_x, v9_y))"
        _maint_Comp1_Ty1_Comp1_dE2_add((v9_x, v9_y))
        # End maint Comp1_Ty1 before "Comp1_dE2.add((v9_x, v9_y))"
        Comp1_dE2.add((v9_x, v9_y))
        # Begin maint _m_Comp1_dE2_out after "Comp1_dE2.add((v9_x, v9_y))"
        _maint__m_Comp1_dE2_out_add((v9_x, v9_y))
        # End maint _m_Comp1_dE2_out after "Comp1_dE2.add((v9_x, v9_y))"

def _maint_Comp1_dE2_Comp1_Tx1_remove(_e):
    # Iterate {(v10_x, v10_y) : v10_x in deltamatch(Comp1_Tx1, 'b', _e, 0), (v10_x, v10_y) in E}
    v10_x = _e
    for v10_y in (_m_E_out[v10_x] if (v10_x in _m_E_out) else set()):
        # Begin maint _m_Comp1_dE2_out before "Comp1_dE2.remove((v10_x, v10_y))"
        _maint__m_Comp1_dE2_out_remove((v10_x, v10_y))
        # End maint _m_Comp1_dE2_out before "Comp1_dE2.remove((v10_x, v10_y))"
        Comp1_dE2.remove((v10_x, v10_y))
        # Begin maint Comp1_Ty1 after "Comp1_dE2.remove((v10_x, v10_y))"
        _maint_Comp1_Ty1_Comp1_dE2_remove((v10_x, v10_y))
        # End maint Comp1_Ty1 after "Comp1_dE2.remove((v10_x, v10_y))"

def _maint_Comp1_dE2_E_add(_e):
    # Iterate {(v11_x, v11_y) : v11_x in Comp1_Tx1, (v11_x, v11_y) in deltamatch(E, 'bb', _e, 0)}
    (v11_x, v11_y) = _e
    if (v11_x in Comp1_Tx1):
        # Begin maint Comp1_Ty1 before "Comp1_dE2.add((v11_x, v11_y))"
        _maint_Comp1_Ty1_Comp1_dE2_add((v11_x, v11_y))
        # End maint Comp1_Ty1 before "Comp1_dE2.add((v11_x, v11_y))"
        Comp1_dE2.add((v11_x, v11_y))
        # Begin maint _m_Comp1_dE2_out after "Comp1_dE2.add((v11_x, v11_y))"
        _maint__m_Comp1_dE2_out_add((v11_x, v11_y))
        # End maint _m_Comp1_dE2_out after "Comp1_dE2.add((v11_x, v11_y))"

Comp1_Tx1 = RCSet()
def _maint_Comp1_Tx1_E_add(_e):
    # Iterate {v7_x : (v7_x, v7_x) in deltamatch(E, 'b1', _e, 0)}
    for v7_x in setmatch({_e}, 'u1', ()):
        # Begin maint Comp1_dE2 before "Comp1_Tx1.add(v7_x)"
        _maint_Comp1_dE2_Comp1_Tx1_add(v7_x)
        # End maint Comp1_dE2 before "Comp1_Tx1.add(v7_x)"
        Comp1_Tx1.add(v7_x)

Comp1 = RCSet()
def _maint_Comp1__U_Comp1_add(_e):
    # Iterate {(v1_x, v1_y, v1_z) : _ in deltamatch(_U_Comp1, 'w', _e, 0), (v1_x, v1_x) in E, (v1_x, v1_y) in Comp1_dE2, (v1_y, v1_z) in Comp1_dS}
    for _ in setmatch(({_e} if ((_m__U_Comp1_w[()] if (() in _m__U_Comp1_w) else RCSet()).getref(()) == 0) else {}), 'w', ()):
        for v1_x in (_m_E_u1[()] if (() in _m_E_u1) else set()):
            for v1_y in (_m_Comp1_dE2_out[v1_x] if (v1_x in _m_Comp1_dE2_out) else set()):
                for v1_z in (_m_Comp1_dS_out[v1_y] if (v1_y in _m_Comp1_dS_out) else set()):
                    if (v1_z not in Comp1):
                        Comp1.add(v1_z)
                    else:
                        Comp1.incref(v1_z)

def _maint_Comp1__U_Comp1_remove(_e):
    # Iterate {(v2_x, v2_y, v2_z) : _ in deltamatch(_U_Comp1, 'w', _e, 0), (v2_x, v2_x) in E, (v2_x, v2_y) in Comp1_dE2, (v2_y, v2_z) in Comp1_dS}
    for _ in setmatch(({_e} if ((_m__U_Comp1_w[()] if (() in _m__U_Comp1_w) else RCSet()).getref(()) == 0) else {}), 'w', ()):
        for v2_x in (_m_E_u1[()] if (() in _m_E_u1) else set()):
            for v2_y in (_m_Comp1_dE2_out[v2_x] if (v2_x in _m_Comp1_dE2_out) else set()):
                for v2_z in (_m_Comp1_dS_out[v2_y] if (v2_y in _m_Comp1_dS_out) else set()):
                    if (Comp1.getref(v2_z) == 1):
                        Comp1.remove(v2_z)
                    else:
                        Comp1.decref(v2_z)

def _maint_Comp1_E_add(_e):
    # Iterate {(v3_x, v3_y, v3_z) : _ in _U_Comp1, (v3_x, v3_x) in deltamatch(E, 'b1', _e, 0), (v3_x, v3_y) in ((Comp1_dE2 - {_e}) + {_e}), (v3_y, v3_z) in Comp1_dS}
    for v3_x in setmatch({_e}, 'u1', ()):
        for v3_y in (_m_Comp1_dE2_out[v3_x] if (v3_x in _m_Comp1_dE2_out) else set()):
            if ((v3_x, v3_y) != _e):
                for v3_z in (_m_Comp1_dS_out[v3_y] if (v3_y in _m_Comp1_dS_out) else set()):
                    for _ in (_m__U_Comp1_w[()] if (() in _m__U_Comp1_w) else RCSet()):
                        if (v3_z not in Comp1):
                            Comp1.add(v3_z)
                        else:
                            Comp1.incref(v3_z)
        for v3_y in setmatch({_e}, 'bu', v3_x):
            for v3_z in (_m_Comp1_dS_out[v3_y] if (v3_y in _m_Comp1_dS_out) else set()):
                for _ in (_m__U_Comp1_w[()] if (() in _m__U_Comp1_w) else RCSet()):
                    if (v3_z not in Comp1):
                        Comp1.add(v3_z)
                    else:
                        Comp1.incref(v3_z)
    # Iterate {(v3_x, v3_y, v3_z) : _ in _U_Comp1, (v3_x, v3_x) in E, (v3_x, v3_y) in deltamatch(Comp1_dE2, 'bb', _e, 0), (v3_x, v3_y) in Comp1_dE2, (v3_y, v3_z) in Comp1_dS}
    (v3_x, v3_y) = _e
    for _ in (_m_E_b1[v3_x] if (v3_x in _m_E_b1) else set()):
        if ((v3_x, v3_y) in Comp1_dE2):
            for v3_z in (_m_Comp1_dS_out[v3_y] if (v3_y in _m_Comp1_dS_out) else set()):
                for _ in (_m__U_Comp1_w[()] if (() in _m__U_Comp1_w) else RCSet()):
                    if (v3_z not in Comp1):
                        Comp1.add(v3_z)
                    else:
                        Comp1.incref(v3_z)

def _maint_Comp1_S_add(_e):
    # Iterate {(v5_x, v5_y, v5_z) : _ in _U_Comp1, (v5_x, v5_x) in E, (v5_x, v5_y) in E, (v5_y, v5_z) in deltamatch(Comp1_dS, 'bb', _e, 0), (v5_y, v5_z) in Comp1_dS}
    (v5_y, v5_z) = _e
    if ((v5_y, v5_z) in Comp1_dS):
        for v5_x in (_m_E_u1[()] if (() in _m_E_u1) else set()):
            if ((v5_x, v5_y) in E):
                for _ in (_m__U_Comp1_w[()] if (() in _m__U_Comp1_w) else RCSet()):
                    if (v5_z not in Comp1):
                        Comp1.add(v5_z)
                    else:
                        Comp1.incref(v5_z)

def _maint_Comp1_S_remove(_e):
    # Iterate {(v6_x, v6_y, v6_z) : _ in _U_Comp1, (v6_x, v6_x) in E, (v6_x, v6_y) in E, (v6_y, v6_z) in deltamatch(Comp1_dS, 'bb', _e, 0), (v6_y, v6_z) in Comp1_dS}
    (v6_y, v6_z) = _e
    if ((v6_y, v6_z) in Comp1_dS):
        for v6_x in (_m_E_u1[()] if (() in _m_E_u1) else set()):
            if ((v6_x, v6_y) in E):
                for _ in (_m__U_Comp1_w[()] if (() in _m__U_Comp1_w) else RCSet()):
                    if (Comp1.getref(v6_z) == 1):
                        Comp1.remove(v6_z)
                    else:
                        Comp1.decref(v6_z)

_U_Comp1 = RCSet()
_UEXT_Comp1 = Set()
def demand_Comp1():
    '{z : _ in _U_Comp1, (x, x) in E, (x, y) in E, (y, z) in S}'
    if (() not in _U_Comp1):
        # Begin maint Comp1 before "_U_Comp1.add(())"
        _maint_Comp1__U_Comp1_add(())
        # End maint Comp1 before "_U_Comp1.add(())"
        _U_Comp1.add(())
        # Begin maint _m__U_Comp1_w after "_U_Comp1.add(())"
        _maint__m__U_Comp1_w_add(())
        # End maint _m__U_Comp1_w after "_U_Comp1.add(())"
    else:
        _U_Comp1.incref(())

def undemand_Comp1():
    '{z : _ in _U_Comp1, (x, x) in E, (x, y) in E, (y, z) in S}'
    if (_U_Comp1.getref(()) == 1):
        # Begin maint _m__U_Comp1_w before "_U_Comp1.remove(())"
        _maint__m__U_Comp1_w_remove(())
        # End maint _m__U_Comp1_w before "_U_Comp1.remove(())"
        _U_Comp1.remove(())
        # Begin maint Comp1 after "_U_Comp1.remove(())"
        _maint_Comp1__U_Comp1_remove(())
        # End maint Comp1 after "_U_Comp1.remove(())"
    else:
        _U_Comp1.decref(())

def query_Comp1():
    '{z : _ in _U_Comp1, (x, x) in E, (x, y) in E, (y, z) in S}'
    if (() not in _UEXT_Comp1):
        _UEXT_Comp1.add(())
        demand_Comp1()
    return True

E = Set()
print(sorted((query_Comp1() and Comp1)))
# Begin maint Comp1_dS before "S.add((1, 2))"
_maint_Comp1_dS_S_add((1, 2))
# End maint Comp1_dS before "S.add((1, 2))"
# Begin maint Comp1 before "S.add((1, 2))"
_maint_Comp1_S_add((1, 2))
# End maint Comp1 before "S.add((1, 2))"
# Begin maint _m_S_out after "S.add((1, 2))"
_maint__m_S_out_add((1, 2))
# End maint _m_S_out after "S.add((1, 2))"
# Begin maint Comp1_Tx1 before "E.add((1, 1))"
_maint_Comp1_Tx1_E_add((1, 1))
# End maint Comp1_Tx1 before "E.add((1, 1))"
# Begin maint Comp1_dE2 before "E.add((1, 1))"
_maint_Comp1_dE2_E_add((1, 1))
# End maint Comp1_dE2 before "E.add((1, 1))"
# Begin maint Comp1 before "E.add((1, 1))"
_maint_Comp1_E_add((1, 1))
# End maint Comp1 before "E.add((1, 1))"
E.add((1, 1))
# Begin maint _m_E_b1 after "E.add((1, 1))"
_maint__m_E_b1_add((1, 1))
# End maint _m_E_b1 after "E.add((1, 1))"
# Begin maint _m_E_u1 after "E.add((1, 1))"
_maint__m_E_u1_add((1, 1))
# End maint _m_E_u1 after "E.add((1, 1))"
# Begin maint _m_E_out after "E.add((1, 1))"
_maint__m_E_out_add((1, 1))
# End maint _m_E_out after "E.add((1, 1))"
print(sorted((query_Comp1() and Comp1)))
# Begin maint _m_S_out before "S.remove((1, 2))"
_maint__m_S_out_remove((1, 2))
# End maint _m_S_out before "S.remove((1, 2))"
# Begin maint Comp1 after "S.remove((1, 2))"
_maint_Comp1_S_remove((1, 2))
# End maint Comp1 after "S.remove((1, 2))"
# Begin maint Comp1_dS after "S.remove((1, 2))"
_maint_Comp1_dS_S_remove((1, 2))
# End maint Comp1_dS after "S.remove((1, 2))"
print(sorted((query_Comp1() and Comp1)))