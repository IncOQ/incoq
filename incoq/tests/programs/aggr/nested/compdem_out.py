from incoq.runtime import *
# Aggr1 := sum(S, None)
# Comp1 := {(x, y) : x in _U_Comp1, (x, y) in E, _av1 in {Aggr1.smlookup('u', (), None)}, (y < _av1)}
# Comp1_Tx1 := {x : x in _U_Comp1}
# Comp1_dE := {(x, y) : x in Comp1_Tx1, (x, y) in E}
# Aggr1_delta := {() : _ in _U_Comp1}
_m_Comp1_out = Map()
def _maint__m_Comp1_out_add(_e):
    (v32_1, v32_2) = _e
    if (v32_1 not in _m_Comp1_out):
        _m_Comp1_out[v32_1] = set()
    _m_Comp1_out[v32_1].add(v32_2)

def _maint__m_Comp1_out_remove(_e):
    (v33_1, v33_2) = _e
    _m_Comp1_out[v33_1].remove(v33_2)
    if (len(_m_Comp1_out[v33_1]) == 0):
        del _m_Comp1_out[v33_1]

_m_S_u = Map()
def _maint__m_S_u_add(_e):
    v30_1 = _e
    if (() not in _m_S_u):
        _m_S_u[()] = set()
    _m_S_u[()].add(v30_1)

_m_Aggr1_u = Map()
def _maint__m_Aggr1_u_add(_e):
    v28_1 = _e
    if (() not in _m_Aggr1_u):
        _m_Aggr1_u[()] = set()
    _m_Aggr1_u[()].add(v28_1)

def _maint__m_Aggr1_u_remove(_e):
    v29_1 = _e
    _m_Aggr1_u[()].remove(v29_1)
    if (len(_m_Aggr1_u[()]) == 0):
        del _m_Aggr1_u[()]

_m_Comp1_dE_out = Map()
def _maint__m_Comp1_dE_out_add(_e):
    (v26_1, v26_2) = _e
    if (v26_1 not in _m_Comp1_dE_out):
        _m_Comp1_dE_out[v26_1] = set()
    _m_Comp1_dE_out[v26_1].add(v26_2)

def _maint__m_Comp1_dE_out_remove(_e):
    (v27_1, v27_2) = _e
    _m_Comp1_dE_out[v27_1].remove(v27_2)
    if (len(_m_Comp1_dE_out[v27_1]) == 0):
        del _m_Comp1_dE_out[v27_1]

_m_E_out = Map()
def _maint__m_E_out_add(_e):
    (v24_1, v24_2) = _e
    if (v24_1 not in _m_E_out):
        _m_E_out[v24_1] = set()
    _m_E_out[v24_1].add(v24_2)

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

Aggr1_delta = Set()
def _maint_Aggr1_delta__U_Comp1_add(_e):
    # Iterate {() : _ in deltamatch(_U_Comp1, 'w', _e, 1)}
    for _ in setmatch(({_e} if ((_m__U_Comp1_w[()] if (() in _m__U_Comp1_w) else RCSet()).getref(()) == 1) else {}), 'w', ()):
        Aggr1_delta.add(())

Comp1_dE = Set()
def _maint_Comp1_dE_Comp1_Tx1_add(_e):
    # Iterate {(v13_x, v13_y) : v13_x in deltamatch(Comp1_Tx1, 'b', _e, 1), (v13_x, v13_y) in E}
    v13_x = _e
    for v13_y in (_m_E_out[v13_x] if (v13_x in _m_E_out) else set()):
        Comp1_dE.add((v13_x, v13_y))
        # Begin maint _m_Comp1_dE_out after "Comp1_dE.add((v13_x, v13_y))"
        _maint__m_Comp1_dE_out_add((v13_x, v13_y))
        # End maint _m_Comp1_dE_out after "Comp1_dE.add((v13_x, v13_y))"

def _maint_Comp1_dE_Comp1_Tx1_remove(_e):
    # Iterate {(v14_x, v14_y) : v14_x in deltamatch(Comp1_Tx1, 'b', _e, 1), (v14_x, v14_y) in E}
    v14_x = _e
    for v14_y in (_m_E_out[v14_x] if (v14_x in _m_E_out) else set()):
        # Begin maint _m_Comp1_dE_out before "Comp1_dE.remove((v14_x, v14_y))"
        _maint__m_Comp1_dE_out_remove((v14_x, v14_y))
        # End maint _m_Comp1_dE_out before "Comp1_dE.remove((v14_x, v14_y))"
        Comp1_dE.remove((v14_x, v14_y))

def _maint_Comp1_dE_E_add(_e):
    # Iterate {(v15_x, v15_y) : v15_x in Comp1_Tx1, (v15_x, v15_y) in deltamatch(E, 'bb', _e, 1)}
    (v15_x, v15_y) = _e
    if (v15_x in Comp1_Tx1):
        Comp1_dE.add((v15_x, v15_y))
        # Begin maint _m_Comp1_dE_out after "Comp1_dE.add((v15_x, v15_y))"
        _maint__m_Comp1_dE_out_add((v15_x, v15_y))
        # End maint _m_Comp1_dE_out after "Comp1_dE.add((v15_x, v15_y))"

Comp1_Tx1 = Set()
def _maint_Comp1_Tx1__U_Comp1_add(_e):
    # Iterate {v11_x : v11_x in deltamatch(_U_Comp1, 'b', _e, 1)}
    v11_x = _e
    Comp1_Tx1.add(v11_x)
    # Begin maint Comp1_dE after "Comp1_Tx1.add(v11_x)"
    _maint_Comp1_dE_Comp1_Tx1_add(v11_x)
    # End maint Comp1_dE after "Comp1_Tx1.add(v11_x)"

def _maint_Comp1_Tx1__U_Comp1_remove(_e):
    # Iterate {v12_x : v12_x in deltamatch(_U_Comp1, 'b', _e, 1)}
    v12_x = _e
    # Begin maint Comp1_dE before "Comp1_Tx1.remove(v12_x)"
    _maint_Comp1_dE_Comp1_Tx1_remove(v12_x)
    # End maint Comp1_dE before "Comp1_Tx1.remove(v12_x)"
    Comp1_Tx1.remove(v12_x)

Comp1 = RCSet()
def _maint_Comp1__U_Comp1_add(_e):
    # Iterate {(v5_x, v5_y, v5__av1) : v5_x in deltamatch(_U_Comp1, 'b', _e, 1), (v5_x, v5_y) in Comp1_dE, v5__av1 in {Aggr1.smlookup('u', (), None)}, (v5_y < v5__av1)}
    v5_x = _e
    for v5__av1 in Aggr1:
        for v5_y in (_m_Comp1_dE_out[v5_x] if (v5_x in _m_Comp1_dE_out) else set()):
            if (v5_y < v5__av1):
                if ((v5_x, v5_y) not in Comp1):
                    Comp1.add((v5_x, v5_y))
                    # Begin maint _m_Comp1_out after "Comp1.add((v5_x, v5_y))"
                    _maint__m_Comp1_out_add((v5_x, v5_y))
                    # End maint _m_Comp1_out after "Comp1.add((v5_x, v5_y))"
                else:
                    Comp1.incref((v5_x, v5_y))

def _maint_Comp1__U_Comp1_remove(_e):
    # Iterate {(v6_x, v6_y, v6__av1) : v6_x in deltamatch(_U_Comp1, 'b', _e, 1), (v6_x, v6_y) in Comp1_dE, v6__av1 in {Aggr1.smlookup('u', (), None)}, (v6_y < v6__av1)}
    v6_x = _e
    for v6__av1 in Aggr1:
        for v6_y in (_m_Comp1_dE_out[v6_x] if (v6_x in _m_Comp1_dE_out) else set()):
            if (v6_y < v6__av1):
                if (Comp1.getref((v6_x, v6_y)) == 1):
                    # Begin maint _m_Comp1_out before "Comp1.remove((v6_x, v6_y))"
                    _maint__m_Comp1_out_remove((v6_x, v6_y))
                    # End maint _m_Comp1_out before "Comp1.remove((v6_x, v6_y))"
                    Comp1.remove((v6_x, v6_y))
                else:
                    Comp1.decref((v6_x, v6_y))

def _maint_Comp1_E_add(_e):
    # Iterate {(v7_x, v7_y, v7__av1) : v7_x in _U_Comp1, (v7_x, v7_y) in deltamatch(Comp1_dE, 'bb', _e, 1), (v7_x, v7_y) in Comp1_dE, v7__av1 in {Aggr1.smlookup('u', (), None)}, (v7_y < v7__av1)}
    (v7_x, v7_y) = _e
    if (v7_x in _U_Comp1):
        if ((v7_x, v7_y) in Comp1_dE):
            for v7__av1 in Aggr1:
                if (v7_y < v7__av1):
                    if ((v7_x, v7_y) not in Comp1):
                        Comp1.add((v7_x, v7_y))
                        # Begin maint _m_Comp1_out after "Comp1.add((v7_x, v7_y))"
                        _maint__m_Comp1_out_add((v7_x, v7_y))
                        # End maint _m_Comp1_out after "Comp1.add((v7_x, v7_y))"
                    else:
                        Comp1.incref((v7_x, v7_y))

def _maint_Comp1_Aggr1_add(_e):
    # Iterate {(v9_x, v9_y, v9__av1) : v9_x in _U_Comp1, (v9_x, v9_y) in Comp1_dE, v9__av1 in deltamatch(Aggr1, 'b', _e, 1), (v9_y < v9__av1)}
    v9__av1 = _e
    for v9_x in _U_Comp1:
        for v9_y in (_m_Comp1_dE_out[v9_x] if (v9_x in _m_Comp1_dE_out) else set()):
            if (v9_y < v9__av1):
                if ((v9_x, v9_y) not in Comp1):
                    Comp1.add((v9_x, v9_y))
                    # Begin maint _m_Comp1_out after "Comp1.add((v9_x, v9_y))"
                    _maint__m_Comp1_out_add((v9_x, v9_y))
                    # End maint _m_Comp1_out after "Comp1.add((v9_x, v9_y))"
                else:
                    Comp1.incref((v9_x, v9_y))

def _maint_Comp1_Aggr1_remove(_e):
    # Iterate {(v10_x, v10_y, v10__av1) : v10_x in _U_Comp1, (v10_x, v10_y) in Comp1_dE, v10__av1 in deltamatch(Aggr1, 'b', _e, 1), (v10_y < v10__av1)}
    v10__av1 = _e
    for v10_x in _U_Comp1:
        for v10_y in (_m_Comp1_dE_out[v10_x] if (v10_x in _m_Comp1_dE_out) else set()):
            if (v10_y < v10__av1):
                if (Comp1.getref((v10_x, v10_y)) == 1):
                    # Begin maint _m_Comp1_out before "Comp1.remove((v10_x, v10_y))"
                    _maint__m_Comp1_out_remove((v10_x, v10_y))
                    # End maint _m_Comp1_out before "Comp1.remove((v10_x, v10_y))"
                    Comp1.remove((v10_x, v10_y))
                else:
                    Comp1.decref((v10_x, v10_y))

_U_Comp1 = RCSet()
_UEXT_Comp1 = Set()
def demand_Comp1(x):
    "{(x, y) : x in _U_Comp1, (x, y) in E, _av1 in {Aggr1.smlookup('u', (), None)}, (y < _av1)}"
    if (x not in _U_Comp1):
        _U_Comp1.add(x)
        # Begin maint _m__U_Comp1_w after "_U_Comp1.add(x)"
        _maint__m__U_Comp1_w_add(x)
        # End maint _m__U_Comp1_w after "_U_Comp1.add(x)"
        # Begin maint Aggr1_delta after "_U_Comp1.add(x)"
        _maint_Aggr1_delta__U_Comp1_add(x)
        # End maint Aggr1_delta after "_U_Comp1.add(x)"
        # Begin maint Comp1_Tx1 after "_U_Comp1.add(x)"
        _maint_Comp1_Tx1__U_Comp1_add(x)
        # End maint Comp1_Tx1 after "_U_Comp1.add(x)"
        # Begin maint Comp1 after "_U_Comp1.add(x)"
        _maint_Comp1__U_Comp1_add(x)
        # End maint Comp1 after "_U_Comp1.add(x)"
        # Begin maint demand_Aggr1 after "_U_Comp1.add(x)"
        for _ in Aggr1_delta.elements():
            demand_Aggr1()
        Aggr1_delta.clear()
        # End maint demand_Aggr1 after "_U_Comp1.add(x)"
    else:
        _U_Comp1.incref(x)

def undemand_Comp1(x):
    "{(x, y) : x in _U_Comp1, (x, y) in E, _av1 in {Aggr1.smlookup('u', (), None)}, (y < _av1)}"
    if (_U_Comp1.getref(x) == 1):
        # Begin maint Comp1 before "_U_Comp1.remove(x)"
        _maint_Comp1__U_Comp1_remove(x)
        # End maint Comp1 before "_U_Comp1.remove(x)"
        # Begin maint Comp1_Tx1 before "_U_Comp1.remove(x)"
        _maint_Comp1_Tx1__U_Comp1_remove(x)
        # End maint Comp1_Tx1 before "_U_Comp1.remove(x)"
        # Begin maint Aggr1_delta before "_U_Comp1.remove(x)"
        _maint_Aggr1_delta__U_Comp1_add(x)
        # End maint Aggr1_delta before "_U_Comp1.remove(x)"
        # Begin maint _m__U_Comp1_w before "_U_Comp1.remove(x)"
        _maint__m__U_Comp1_w_remove(x)
        # End maint _m__U_Comp1_w before "_U_Comp1.remove(x)"
        _U_Comp1.remove(x)
        # Begin maint undemand_Aggr1 after "_U_Comp1.remove(x)"
        for _ in Aggr1_delta.elements():
            undemand_Aggr1()
        Aggr1_delta.clear()
        # End maint undemand_Aggr1 after "_U_Comp1.remove(x)"
    else:
        _U_Comp1.decref(x)

def query_Comp1(x):
    "{(x, y) : x in _U_Comp1, (x, y) in E, _av1 in {Aggr1.smlookup('u', (), None)}, (y < _av1)}"
    if (x not in _UEXT_Comp1):
        _UEXT_Comp1.add(x)
        demand_Comp1(x)
    return True

Aggr1 = Set()
def _maint_Aggr1_add(_e):
    v1_v1 = _e
    if (() in _U_Aggr1):
        v1_val = _m_Aggr1_u.singlelookup(())
        v1_val = (v1_val + v1_v1)
        v1_elem = _m_Aggr1_u.singlelookup(())
        # Begin maint Comp1 before "Aggr1.remove(v1_elem)"
        _maint_Comp1_Aggr1_remove(v1_elem)
        # End maint Comp1 before "Aggr1.remove(v1_elem)"
        # Begin maint _m_Aggr1_u before "Aggr1.remove(v1_elem)"
        _maint__m_Aggr1_u_remove(v1_elem)
        # End maint _m_Aggr1_u before "Aggr1.remove(v1_elem)"
        Aggr1.remove(v1_elem)
        Aggr1.add(v1_val)
        # Begin maint _m_Aggr1_u after "Aggr1.add(v1_val)"
        _maint__m_Aggr1_u_add(v1_val)
        # End maint _m_Aggr1_u after "Aggr1.add(v1_val)"
        # Begin maint Comp1 after "Aggr1.add(v1_val)"
        _maint_Comp1_Aggr1_add(v1_val)
        # End maint Comp1 after "Aggr1.add(v1_val)"

_U_Aggr1 = RCSet()
_UEXT_Aggr1 = Set()
def demand_Aggr1():
    'sum(S, None)'
    if (() not in _U_Aggr1):
        _U_Aggr1.add(())
        # Begin maint Aggr1 after "_U_Aggr1.add(())"
        v3_val = 0
        for v3_elem in (_m_S_u[()] if (() in _m_S_u) else set()):
            v3_val = (v3_val + v3_elem)
        Aggr1.add(v3_val)
        # Begin maint _m_Aggr1_u after "Aggr1.add(v3_val)"
        _maint__m_Aggr1_u_add(v3_val)
        # End maint _m_Aggr1_u after "Aggr1.add(v3_val)"
        # Begin maint Comp1 after "Aggr1.add(v3_val)"
        _maint_Comp1_Aggr1_add(v3_val)
        # End maint Comp1 after "Aggr1.add(v3_val)"
        # End maint Aggr1 after "_U_Aggr1.add(())"
    else:
        _U_Aggr1.incref(())

def undemand_Aggr1():
    'sum(S, None)'
    if (_U_Aggr1.getref(()) == 1):
        # Begin maint Aggr1 before "_U_Aggr1.remove(())"
        v4_elem = _m_Aggr1_u.singlelookup(())
        # Begin maint Comp1 before "Aggr1.remove(v4_elem)"
        _maint_Comp1_Aggr1_remove(v4_elem)
        # End maint Comp1 before "Aggr1.remove(v4_elem)"
        # Begin maint _m_Aggr1_u before "Aggr1.remove(v4_elem)"
        _maint__m_Aggr1_u_remove(v4_elem)
        # End maint _m_Aggr1_u before "Aggr1.remove(v4_elem)"
        Aggr1.remove(v4_elem)
        # End maint Aggr1 before "_U_Aggr1.remove(())"
        _U_Aggr1.remove(())
    else:
        _U_Aggr1.decref(())

def query_Aggr1():
    'sum(S, None)'
    if (() not in _UEXT_Aggr1):
        _UEXT_Aggr1.add(())
        demand_Aggr1()
    return True

for e in [1, 2, 3, 4]:
    # Begin maint _m_S_u after "S.add(e)"
    _maint__m_S_u_add(e)
    # End maint _m_S_u after "S.add(e)"
    # Begin maint Aggr1 after "S.add(e)"
    _maint_Aggr1_add(e)
    # End maint Aggr1 after "S.add(e)"
for e in [(1, 5), (1, 8), (1, 15), (2, 9), (2, 18)]:
    # Begin maint _m_E_out after "E.add(e)"
    _maint__m_E_out_add(e)
    # End maint _m_E_out after "E.add(e)"
    # Begin maint Comp1_dE after "E.add(e)"
    _maint_Comp1_dE_E_add(e)
    # End maint Comp1_dE after "E.add(e)"
    # Begin maint Comp1 after "E.add(e)"
    _maint_Comp1_E_add(e)
    # End maint Comp1 after "E.add(e)"
    # Begin maint demand_Aggr1 after "E.add(e)"
    for _ in Aggr1_delta.elements():
        demand_Aggr1()
    Aggr1_delta.clear()
    # End maint demand_Aggr1 after "E.add(e)"
x = 1
print(sorted((query_Comp1(x) and (_m_Comp1_out[x] if (x in _m_Comp1_out) else set()))))