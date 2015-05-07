from incoq.runtime import *
# Comp1 := {(x, y) : x in _U_Comp1, (x, y) in E}
# Aggr1 := sum(DEMQUERY(Comp1, [x], setmatch(Comp1, 'bu', x)), None)
_m_E_out = Map()
def _maint__m_E_out_add(_e):
    (v13_1, v13_2) = _e
    if (v13_1 not in _m_E_out):
        _m_E_out[v13_1] = set()
    _m_E_out[v13_1].add(v13_2)

_m_Comp1_out = Map()
def _maint__m_Comp1_out_add(_e):
    (v11_1, v11_2) = _e
    if (v11_1 not in _m_Comp1_out):
        _m_Comp1_out[v11_1] = set()
    _m_Comp1_out[v11_1].add(v11_2)

def _maint__m_Comp1_out_remove(_e):
    (v12_1, v12_2) = _e
    _m_Comp1_out[v12_1].remove(v12_2)
    if (len(_m_Comp1_out[v12_1]) == 0):
        del _m_Comp1_out[v12_1]

_m_Aggr1_out = Map()
def _maint__m_Aggr1_out_add(_e):
    (v9_1, v9_2) = _e
    if (v9_1 not in _m_Aggr1_out):
        _m_Aggr1_out[v9_1] = set()
    _m_Aggr1_out[v9_1].add(v9_2)

def _maint__m_Aggr1_out_remove(_e):
    (v10_1, v10_2) = _e
    _m_Aggr1_out[v10_1].remove(v10_2)
    if (len(_m_Aggr1_out[v10_1]) == 0):
        del _m_Aggr1_out[v10_1]

def _maint_Aggr1_add(_e):
    (v5_v1, v5_v2) = _e
    if (v5_v1 in _U_Aggr1):
        v5_val = _m_Aggr1_out.singlelookup(v5_v1)
        v5_val = (v5_val + v5_v2)
        v5_1 = v5_v1
        v5_elem = _m_Aggr1_out.singlelookup(v5_v1)
        # Begin maint _m_Aggr1_out before "Aggr1.remove((v5_1, v5_elem))"
        _maint__m_Aggr1_out_remove((v5_1, v5_elem))
        # End maint _m_Aggr1_out before "Aggr1.remove((v5_1, v5_elem))"
        # Begin maint _m_Aggr1_out after "Aggr1.add((v5_1, v5_val))"
        _maint__m_Aggr1_out_add((v5_1, v5_val))
        # End maint _m_Aggr1_out after "Aggr1.add((v5_1, v5_val))"

def _maint_Aggr1_remove(_e):
    (v6_v1, v6_v2) = _e
    if (v6_v1 in _U_Aggr1):
        v6_val = _m_Aggr1_out.singlelookup(v6_v1)
        v6_val = (v6_val - v6_v2)
        v6_1 = v6_v1
        v6_elem = _m_Aggr1_out.singlelookup(v6_v1)
        # Begin maint _m_Aggr1_out before "Aggr1.remove((v6_1, v6_elem))"
        _maint__m_Aggr1_out_remove((v6_1, v6_elem))
        # End maint _m_Aggr1_out before "Aggr1.remove((v6_1, v6_elem))"
        # Begin maint _m_Aggr1_out after "Aggr1.add((v6_1, v6_val))"
        _maint__m_Aggr1_out_add((v6_1, v6_val))
        # End maint _m_Aggr1_out after "Aggr1.add((v6_1, v6_val))"

_U_Aggr1 = RCSet()
_UEXT_Aggr1 = LRUSet()
def demand_Aggr1(x):
    "sum(DEMQUERY(Comp1, [x], setmatch(Comp1, 'bu', x)), None)"
    if (x not in _U_Aggr1):
        _U_Aggr1.add(x)
        # Begin maint Aggr1 after "_U_Aggr1.add(x)"
        v7_val = 0
        for v7_elem in (_m_Comp1_out[x] if (x in _m_Comp1_out) else set()):
            v7_val = (v7_val + v7_elem)
        v7_1 = x
        # Begin maint _m_Aggr1_out after "Aggr1.add((v7_1, v7_val))"
        _maint__m_Aggr1_out_add((v7_1, v7_val))
        # End maint _m_Aggr1_out after "Aggr1.add((v7_1, v7_val))"
        demand_Comp1(x)
        # End maint Aggr1 after "_U_Aggr1.add(x)"
    else:
        _U_Aggr1.incref(x)

def undemand_Aggr1(x):
    "sum(DEMQUERY(Comp1, [x], setmatch(Comp1, 'bu', x)), None)"
    if (_U_Aggr1.getref(x) == 1):
        # Begin maint Aggr1 before "_U_Aggr1.remove(x)"
        undemand_Comp1(x)
        v8_1 = x
        v8_elem = _m_Aggr1_out.singlelookup(x)
        # Begin maint _m_Aggr1_out before "Aggr1.remove((v8_1, v8_elem))"
        _maint__m_Aggr1_out_remove((v8_1, v8_elem))
        # End maint _m_Aggr1_out before "Aggr1.remove((v8_1, v8_elem))"
        # End maint Aggr1 before "_U_Aggr1.remove(x)"
        _U_Aggr1.remove(x)
    else:
        _U_Aggr1.decref(x)

def query_Aggr1(x):
    "sum(DEMQUERY(Comp1, [x], setmatch(Comp1, 'bu', x)), None)"
    if (x not in _UEXT_Aggr1):
        while (len(_UEXT_Aggr1) >= 2):
            _top_v1 = _top = _UEXT_Aggr1.peek()
            undemand_Aggr1(_top_v1)
            _UEXT_Aggr1.remove(_top)
        _UEXT_Aggr1.add(x)
        demand_Aggr1(x)
    else:
        _UEXT_Aggr1.ping(x)
    return True

def _maint_Comp1__U_Comp1_add(_e):
    # Iterate {(v1_x, v1_y) : v1_x in deltamatch(_U_Comp1, 'b', _e, 1), (v1_x, v1_y) in E}
    v1_x = _e
    for v1_y in (_m_E_out[v1_x] if (v1_x in _m_E_out) else set()):
        # Begin maint _m_Comp1_out after "Comp1.add((v1_x, v1_y))"
        _maint__m_Comp1_out_add((v1_x, v1_y))
        # End maint _m_Comp1_out after "Comp1.add((v1_x, v1_y))"
        # Begin maint Aggr1 after "Comp1.add((v1_x, v1_y))"
        _maint_Aggr1_add((v1_x, v1_y))
        # End maint Aggr1 after "Comp1.add((v1_x, v1_y))"

def _maint_Comp1__U_Comp1_remove(_e):
    # Iterate {(v2_x, v2_y) : v2_x in deltamatch(_U_Comp1, 'b', _e, 1), (v2_x, v2_y) in E}
    v2_x = _e
    for v2_y in (_m_E_out[v2_x] if (v2_x in _m_E_out) else set()):
        # Begin maint Aggr1 before "Comp1.remove((v2_x, v2_y))"
        _maint_Aggr1_remove((v2_x, v2_y))
        # End maint Aggr1 before "Comp1.remove((v2_x, v2_y))"
        # Begin maint _m_Comp1_out before "Comp1.remove((v2_x, v2_y))"
        _maint__m_Comp1_out_remove((v2_x, v2_y))
        # End maint _m_Comp1_out before "Comp1.remove((v2_x, v2_y))"

def _maint_Comp1_E_add(_e):
    # Iterate {(v3_x, v3_y) : v3_x in _U_Comp1, (v3_x, v3_y) in deltamatch(E, 'bb', _e, 1)}
    (v3_x, v3_y) = _e
    if (v3_x in _U_Comp1):
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
        _U_Comp1.remove(x)
    else:
        _U_Comp1.decref(x)

def query_Comp1(x):
    '{(x, y) : x in _U_Comp1, (x, y) in E}'
    if (x not in _UEXT_Comp1):
        _UEXT_Comp1.add(x)
        demand_Comp1(x)
    return True

for e in [(1, 2), (1, 3), (2, 4), (2, 10), (3, 1)]:
    # Begin maint _m_E_out after "E.add(e)"
    _maint__m_E_out_add(e)
    # End maint _m_E_out after "E.add(e)"
    # Begin maint Comp1 after "E.add(e)"
    _maint_Comp1_E_add(e)
    # End maint Comp1 after "E.add(e)"
for x in [1, 2, 1, 3]:
    print((query_Aggr1(x) and _m_Aggr1_out.singlelookup(x)))