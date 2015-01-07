from oinc.runtime import *
# Comp1 := {(x, y) : x in _U_Comp1, (x, y) in E}
# Comp1_Tx1 := {x : x in _U_Comp1}
# Comp1_dE := {(x, y) : x in Comp1_Tx1, (x, y) in E}
# Aggr1 := sum(DEMQUERY(Comp1, [x], setmatch(Comp1, 'bu', x)), None)
# Comp12 := {x : x in S, _av1 in {Aggr1.smlookup('bu', x, None)}, (x < _av1)}
# Comp12_Tx := {x : x in S}
# Aggr1_delta := {x : x in Comp12_Tx}
_m_Comp1_dE_out = Map()
def _maint__m_Comp1_dE_out_add(_e):
    (v30_1, v30_2) = _e
    if (v30_1 not in _m_Comp1_dE_out):
        _m_Comp1_dE_out[v30_1] = set()
    _m_Comp1_dE_out[v30_1].add(v30_2)

def _maint__m_Comp1_dE_out_remove(_e):
    (v31_1, v31_2) = _e
    _m_Comp1_dE_out[v31_1].remove(v31_2)
    if (len(_m_Comp1_dE_out[v31_1]) == 0):
        del _m_Comp1_dE_out[v31_1]

_m_E_out = Map()
def _maint__m_E_out_add(_e):
    (v28_1, v28_2) = _e
    if (v28_1 not in _m_E_out):
        _m_E_out[v28_1] = set()
    _m_E_out[v28_1].add(v28_2)

_m_Comp1_out = Map()
def _maint__m_Comp1_out_add(_e):
    (v26_1, v26_2) = _e
    if (v26_1 not in _m_Comp1_out):
        _m_Comp1_out[v26_1] = set()
    _m_Comp1_out[v26_1].add(v26_2)

def _maint__m_Comp1_out_remove(_e):
    (v27_1, v27_2) = _e
    _m_Comp1_out[v27_1].remove(v27_2)
    if (len(_m_Comp1_out[v27_1]) == 0):
        del _m_Comp1_out[v27_1]

_m_Aggr1_out = Map()
def _maint__m_Aggr1_out_add(_e):
    (v24_1, v24_2) = _e
    if (v24_1 not in _m_Aggr1_out):
        _m_Aggr1_out[v24_1] = set()
    _m_Aggr1_out[v24_1].add(v24_2)

def _maint__m_Aggr1_out_remove(_e):
    (v25_1, v25_2) = _e
    _m_Aggr1_out[v25_1].remove(v25_2)
    if (len(_m_Aggr1_out[v25_1]) == 0):
        del _m_Aggr1_out[v25_1]

Aggr1_delta = RCSet()
def _maint_Aggr1_delta_Comp12_Tx_add(_e):
    # Iterate {v21_x : v21_x in deltamatch(Comp12_Tx, 'b', _e, 1)}
    v21_x = _e
    Aggr1_delta.add(v21_x)

def _maint_Comp12_Tx_S_add(_e):
    # Iterate {v19_x : v19_x in deltamatch(S, 'b', _e, 1)}
    v19_x = _e
    # Begin maint Aggr1_delta after "Comp12_Tx.add(v19_x)"
    _maint_Aggr1_delta_Comp12_Tx_add(v19_x)
    # End maint Aggr1_delta after "Comp12_Tx.add(v19_x)"

Comp12 = RCSet()
def _maint_Comp12_S_add(_e):
    # Iterate {(v15_x, v15__av1) : v15_x in deltamatch(S, 'b', _e, 1), v15__av1 in {Aggr1.smlookup('bu', v15_x, None)}, (v15_x < v15__av1)}
    v15_x = _e
    for v15__av1 in (_m_Aggr1_out[v15_x] if (v15_x in _m_Aggr1_out) else set()):
        if (v15_x < v15__av1):
            if (v15_x not in Comp12):
                Comp12.add(v15_x)
            else:
                Comp12.incref(v15_x)

def _maint_Comp12_Aggr1_add(_e):
    # Iterate {(v17_x, v17__av1) : v17_x in S, (v17_x, v17__av1) in deltamatch(Aggr1, 'bb', _e, 1), (v17_x < v17__av1)}
    (v17_x, v17__av1) = _e
    if (v17_x in S):
        if (v17_x < v17__av1):
            if (v17_x not in Comp12):
                Comp12.add(v17_x)
            else:
                Comp12.incref(v17_x)

def _maint_Comp12_Aggr1_remove(_e):
    # Iterate {(v18_x, v18__av1) : v18_x in S, (v18_x, v18__av1) in deltamatch(Aggr1, 'bb', _e, 1), (v18_x < v18__av1)}
    (v18_x, v18__av1) = _e
    if (v18_x in S):
        if (v18_x < v18__av1):
            if (Comp12.getref(v18_x) == 1):
                Comp12.remove(v18_x)
            else:
                Comp12.decref(v18_x)

def _maint_Aggr1_add(_e):
    (v11_v1, v11_v2) = _e
    if (v11_v1 in _U_Aggr1):
        v11_val = _m_Aggr1_out.singlelookup(v11_v1)
        v11_val = (v11_val + v11_v2)
        v11_1 = v11_v1
        v11_elem = _m_Aggr1_out.singlelookup(v11_v1)
        # Begin maint Comp12 before "Aggr1.remove((v11_1, v11_elem))"
        _maint_Comp12_Aggr1_remove((v11_1, v11_elem))
        # End maint Comp12 before "Aggr1.remove((v11_1, v11_elem))"
        # Begin maint _m_Aggr1_out before "Aggr1.remove((v11_1, v11_elem))"
        _maint__m_Aggr1_out_remove((v11_1, v11_elem))
        # End maint _m_Aggr1_out before "Aggr1.remove((v11_1, v11_elem))"
        # Begin maint _m_Aggr1_out after "Aggr1.add((v11_1, v11_val))"
        _maint__m_Aggr1_out_add((v11_1, v11_val))
        # End maint _m_Aggr1_out after "Aggr1.add((v11_1, v11_val))"
        # Begin maint Comp12 after "Aggr1.add((v11_1, v11_val))"
        _maint_Comp12_Aggr1_add((v11_1, v11_val))
        # End maint Comp12 after "Aggr1.add((v11_1, v11_val))"

def _maint_Aggr1_remove(_e):
    (v12_v1, v12_v2) = _e
    if (v12_v1 in _U_Aggr1):
        v12_val = _m_Aggr1_out.singlelookup(v12_v1)
        v12_val = (v12_val - v12_v2)
        v12_1 = v12_v1
        v12_elem = _m_Aggr1_out.singlelookup(v12_v1)
        # Begin maint Comp12 before "Aggr1.remove((v12_1, v12_elem))"
        _maint_Comp12_Aggr1_remove((v12_1, v12_elem))
        # End maint Comp12 before "Aggr1.remove((v12_1, v12_elem))"
        # Begin maint _m_Aggr1_out before "Aggr1.remove((v12_1, v12_elem))"
        _maint__m_Aggr1_out_remove((v12_1, v12_elem))
        # End maint _m_Aggr1_out before "Aggr1.remove((v12_1, v12_elem))"
        # Begin maint _m_Aggr1_out after "Aggr1.add((v12_1, v12_val))"
        _maint__m_Aggr1_out_add((v12_1, v12_val))
        # End maint _m_Aggr1_out after "Aggr1.add((v12_1, v12_val))"
        # Begin maint Comp12 after "Aggr1.add((v12_1, v12_val))"
        _maint_Comp12_Aggr1_add((v12_1, v12_val))
        # End maint Comp12 after "Aggr1.add((v12_1, v12_val))"

_U_Aggr1 = RCSet()
_UEXT_Aggr1 = Set()
def demand_Aggr1(x):
    "sum(DEMQUERY(Comp1, [x], setmatch(Comp1, 'bu', x)), None)"
    if (x not in _U_Aggr1):
        _U_Aggr1.add(x)
        # Begin maint Aggr1 after "_U_Aggr1.add(x)"
        v13_val = 0
        for v13_elem in (_m_Comp1_out[x] if (x in _m_Comp1_out) else set()):
            v13_val = (v13_val + v13_elem)
        v13_1 = x
        # Begin maint _m_Aggr1_out after "Aggr1.add((v13_1, v13_val))"
        _maint__m_Aggr1_out_add((v13_1, v13_val))
        # End maint _m_Aggr1_out after "Aggr1.add((v13_1, v13_val))"
        # Begin maint Comp12 after "Aggr1.add((v13_1, v13_val))"
        _maint_Comp12_Aggr1_add((v13_1, v13_val))
        # End maint Comp12 after "Aggr1.add((v13_1, v13_val))"
        demand_Comp1(x)
        # End maint Aggr1 after "_U_Aggr1.add(x)"
    else:
        _U_Aggr1.incref(x)

def undemand_Aggr1(x):
    "sum(DEMQUERY(Comp1, [x], setmatch(Comp1, 'bu', x)), None)"
    if (_U_Aggr1.getref(x) == 1):
        # Begin maint Aggr1 before "_U_Aggr1.remove(x)"
        undemand_Comp1(x)
        v14_1 = x
        v14_elem = _m_Aggr1_out.singlelookup(x)
        # Begin maint Comp12 before "Aggr1.remove((v14_1, v14_elem))"
        _maint_Comp12_Aggr1_remove((v14_1, v14_elem))
        # End maint Comp12 before "Aggr1.remove((v14_1, v14_elem))"
        # Begin maint _m_Aggr1_out before "Aggr1.remove((v14_1, v14_elem))"
        _maint__m_Aggr1_out_remove((v14_1, v14_elem))
        # End maint _m_Aggr1_out before "Aggr1.remove((v14_1, v14_elem))"
        # End maint Aggr1 before "_U_Aggr1.remove(x)"
        _U_Aggr1.remove(x)
    else:
        _U_Aggr1.decref(x)

def query_Aggr1(x):
    "sum(DEMQUERY(Comp1, [x], setmatch(Comp1, 'bu', x)), None)"
    if (x not in _UEXT_Aggr1):
        _UEXT_Aggr1.add(x)
        demand_Aggr1(x)
    return True

Comp1_dE = RCSet()
def _maint_Comp1_dE_Comp1_Tx1_add(_e):
    # Iterate {(v7_x, v7_y) : v7_x in deltamatch(Comp1_Tx1, 'b', _e, 1), (v7_x, v7_y) in E}
    v7_x = _e
    for v7_y in (_m_E_out[v7_x] if (v7_x in _m_E_out) else set()):
        Comp1_dE.add((v7_x, v7_y))
        # Begin maint _m_Comp1_dE_out after "Comp1_dE.add((v7_x, v7_y))"
        _maint__m_Comp1_dE_out_add((v7_x, v7_y))
        # End maint _m_Comp1_dE_out after "Comp1_dE.add((v7_x, v7_y))"

def _maint_Comp1_dE_Comp1_Tx1_remove(_e):
    # Iterate {(v8_x, v8_y) : v8_x in deltamatch(Comp1_Tx1, 'b', _e, 1), (v8_x, v8_y) in E}
    v8_x = _e
    for v8_y in (_m_E_out[v8_x] if (v8_x in _m_E_out) else set()):
        # Begin maint _m_Comp1_dE_out before "Comp1_dE.remove((v8_x, v8_y))"
        _maint__m_Comp1_dE_out_remove((v8_x, v8_y))
        # End maint _m_Comp1_dE_out before "Comp1_dE.remove((v8_x, v8_y))"
        Comp1_dE.remove((v8_x, v8_y))

def _maint_Comp1_dE_E_add(_e):
    # Iterate {(v9_x, v9_y) : v9_x in Comp1_Tx1, (v9_x, v9_y) in deltamatch(E, 'bb', _e, 1)}
    (v9_x, v9_y) = _e
    if (v9_x in Comp1_Tx1):
        Comp1_dE.add((v9_x, v9_y))
        # Begin maint _m_Comp1_dE_out after "Comp1_dE.add((v9_x, v9_y))"
        _maint__m_Comp1_dE_out_add((v9_x, v9_y))
        # End maint _m_Comp1_dE_out after "Comp1_dE.add((v9_x, v9_y))"

Comp1_Tx1 = RCSet()
def _maint_Comp1_Tx1__U_Comp1_add(_e):
    # Iterate {v5_x : v5_x in deltamatch(_U_Comp1, 'b', _e, 1)}
    v5_x = _e
    Comp1_Tx1.add(v5_x)
    # Begin maint Comp1_dE after "Comp1_Tx1.add(v5_x)"
    _maint_Comp1_dE_Comp1_Tx1_add(v5_x)
    # End maint Comp1_dE after "Comp1_Tx1.add(v5_x)"

def _maint_Comp1_Tx1__U_Comp1_remove(_e):
    # Iterate {v6_x : v6_x in deltamatch(_U_Comp1, 'b', _e, 1)}
    v6_x = _e
    # Begin maint Comp1_dE before "Comp1_Tx1.remove(v6_x)"
    _maint_Comp1_dE_Comp1_Tx1_remove(v6_x)
    # End maint Comp1_dE before "Comp1_Tx1.remove(v6_x)"
    Comp1_Tx1.remove(v6_x)

def _maint_Comp1__U_Comp1_add(_e):
    # Iterate {(v1_x, v1_y) : v1_x in deltamatch(_U_Comp1, 'b', _e, 1), (v1_x, v1_y) in Comp1_dE}
    v1_x = _e
    for v1_y in (_m_Comp1_dE_out[v1_x] if (v1_x in _m_Comp1_dE_out) else set()):
        # Begin maint _m_Comp1_out after "Comp1.add((v1_x, v1_y))"
        _maint__m_Comp1_out_add((v1_x, v1_y))
        # End maint _m_Comp1_out after "Comp1.add((v1_x, v1_y))"
        # Begin maint Aggr1 after "Comp1.add((v1_x, v1_y))"
        _maint_Aggr1_add((v1_x, v1_y))
        # End maint Aggr1 after "Comp1.add((v1_x, v1_y))"

def _maint_Comp1__U_Comp1_remove(_e):
    # Iterate {(v2_x, v2_y) : v2_x in deltamatch(_U_Comp1, 'b', _e, 1), (v2_x, v2_y) in Comp1_dE}
    v2_x = _e
    for v2_y in (_m_Comp1_dE_out[v2_x] if (v2_x in _m_Comp1_dE_out) else set()):
        # Begin maint Aggr1 before "Comp1.remove((v2_x, v2_y))"
        _maint_Aggr1_remove((v2_x, v2_y))
        # End maint Aggr1 before "Comp1.remove((v2_x, v2_y))"
        # Begin maint _m_Comp1_out before "Comp1.remove((v2_x, v2_y))"
        _maint__m_Comp1_out_remove((v2_x, v2_y))
        # End maint _m_Comp1_out before "Comp1.remove((v2_x, v2_y))"

def _maint_Comp1_E_add(_e):
    # Iterate {(v3_x, v3_y) : v3_x in _U_Comp1, (v3_x, v3_y) in deltamatch(Comp1_dE, 'bb', _e, 1), (v3_x, v3_y) in Comp1_dE}
    (v3_x, v3_y) = _e
    if (v3_x in _U_Comp1):
        if ((v3_x, v3_y) in Comp1_dE):
            # Begin maint _m_Comp1_out after "Comp1.add((v3_x, v3_y))"
            _maint__m_Comp1_out_add((v3_x, v3_y))
            # End maint _m_Comp1_out after "Comp1.add((v3_x, v3_y))"
            # Begin maint Aggr1 after "Comp1.add((v3_x, v3_y))"
            _maint_Aggr1_add((v3_x, v3_y))
            # End maint Aggr1 after "Comp1.add((v3_x, v3_y))"

_U_Comp1 = RCSet()
_UEXT_Comp1 = Set()
def demand_Comp1(x):
    '{(x, y) : x in _U_Comp1, (x, y) in E}'
    if (x not in _U_Comp1):
        _U_Comp1.add(x)
        # Begin maint Comp1_Tx1 after "_U_Comp1.add(x)"
        _maint_Comp1_Tx1__U_Comp1_add(x)
        # End maint Comp1_Tx1 after "_U_Comp1.add(x)"
        # Begin maint Comp1 after "_U_Comp1.add(x)"
        _maint_Comp1__U_Comp1_add(x)
        # End maint Comp1 after "_U_Comp1.add(x)"
    else:
        _U_Comp1.incref(x)

def undemand_Comp1(x):
    '{(x, y) : x in _U_Comp1, (x, y) in E}'
    if (_U_Comp1.getref(x) == 1):
        # Begin maint Comp1 before "_U_Comp1.remove(x)"
        _maint_Comp1__U_Comp1_remove(x)
        # End maint Comp1 before "_U_Comp1.remove(x)"
        # Begin maint Comp1_Tx1 before "_U_Comp1.remove(x)"
        _maint_Comp1_Tx1__U_Comp1_remove(x)
        # End maint Comp1_Tx1 before "_U_Comp1.remove(x)"
        _U_Comp1.remove(x)
    else:
        _U_Comp1.decref(x)

def query_Comp1(x):
    '{(x, y) : x in _U_Comp1, (x, y) in E}'
    if (x not in _UEXT_Comp1):
        _UEXT_Comp1.add(x)
        demand_Comp1(x)
    return True

S = Set()
for e in [1, 2, 4, 8]:
    S.add(e)
    # Begin maint Comp12_Tx after "S.add(e)"
    _maint_Comp12_Tx_S_add(e)
    # End maint Comp12_Tx after "S.add(e)"
    # Begin maint Comp12 after "S.add(e)"
    _maint_Comp12_S_add(e)
    # End maint Comp12 after "S.add(e)"
    # Begin maint demand_Aggr1 after "S.add(e)"
    for v23_x in Aggr1_delta.elements():
        demand_Aggr1(v23_x)
    Aggr1_delta.clear()
    # End maint demand_Aggr1 after "S.add(e)"
for e in [(1, 2), (1, 3), (2, 1), (3, 4), (8, 1), (8, 4)]:
    # Begin maint _m_E_out after "E.add(e)"
    _maint__m_E_out_add(e)
    # End maint _m_E_out after "E.add(e)"
    # Begin maint Comp1_dE after "E.add(e)"
    _maint_Comp1_dE_E_add(e)
    # End maint Comp1_dE after "E.add(e)"
    # Begin maint Comp1 after "E.add(e)"
    _maint_Comp1_E_add(e)
    # End maint Comp1 after "E.add(e)"
print(sorted(Comp12))