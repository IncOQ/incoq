from incoq.runtime import *
# Comp1 := {(x, L, y) : L in _U_Comp1, (x, y) in E, (y < L)}
# Aggr1 := sum(DEMQUERY(Comp1, [L], setmatch(Comp1, 'bbu', (x, L))), None)
_m_Comp1_bbu = Map()
def _maint__m_Comp1_bbu_add(_e):
    (v11_1, v11_2, v11_3) = _e
    if ((v11_1, v11_2) not in _m_Comp1_bbu):
        _m_Comp1_bbu[(v11_1, v11_2)] = set()
    _m_Comp1_bbu[(v11_1, v11_2)].add(v11_3)

def _maint__m_Comp1_bbu_remove(_e):
    (v12_1, v12_2, v12_3) = _e
    _m_Comp1_bbu[(v12_1, v12_2)].remove(v12_3)
    if (len(_m_Comp1_bbu[(v12_1, v12_2)]) == 0):
        del _m_Comp1_bbu[(v12_1, v12_2)]

_m_Aggr1_bbu = Map()
def _maint__m_Aggr1_bbu_add(_e):
    (v9_1, v9_2, v9_3) = _e
    if ((v9_1, v9_2) not in _m_Aggr1_bbu):
        _m_Aggr1_bbu[(v9_1, v9_2)] = set()
    _m_Aggr1_bbu[(v9_1, v9_2)].add(v9_3)

def _maint__m_Aggr1_bbu_remove(_e):
    (v10_1, v10_2, v10_3) = _e
    _m_Aggr1_bbu[(v10_1, v10_2)].remove(v10_3)
    if (len(_m_Aggr1_bbu[(v10_1, v10_2)]) == 0):
        del _m_Aggr1_bbu[(v10_1, v10_2)]

def _maint_Aggr1_add(_e):
    (v5_v1, v5_v2, v5_v3) = _e
    if ((v5_v1, v5_v2) in _U_Aggr1):
        v5_val = _m_Aggr1_bbu.singlelookup((v5_v1, v5_v2))
        v5_val = (v5_val + v5_v3)
        (v5_1, v5_2) = (v5_v1, v5_v2)
        v5_elem = _m_Aggr1_bbu.singlelookup((v5_v1, v5_v2))
        # Begin maint _m_Aggr1_bbu before "Aggr1.remove((v5_1, v5_2, v5_elem))"
        _maint__m_Aggr1_bbu_remove((v5_1, v5_2, v5_elem))
        # End maint _m_Aggr1_bbu before "Aggr1.remove((v5_1, v5_2, v5_elem))"
        # Begin maint _m_Aggr1_bbu after "Aggr1.add((v5_1, v5_2, v5_val))"
        _maint__m_Aggr1_bbu_add((v5_1, v5_2, v5_val))
        # End maint _m_Aggr1_bbu after "Aggr1.add((v5_1, v5_2, v5_val))"

def _maint_Aggr1_remove(_e):
    (v6_v1, v6_v2, v6_v3) = _e
    if ((v6_v1, v6_v2) in _U_Aggr1):
        v6_val = _m_Aggr1_bbu.singlelookup((v6_v1, v6_v2))
        v6_val = (v6_val - v6_v3)
        (v6_1, v6_2) = (v6_v1, v6_v2)
        v6_elem = _m_Aggr1_bbu.singlelookup((v6_v1, v6_v2))
        # Begin maint _m_Aggr1_bbu before "Aggr1.remove((v6_1, v6_2, v6_elem))"
        _maint__m_Aggr1_bbu_remove((v6_1, v6_2, v6_elem))
        # End maint _m_Aggr1_bbu before "Aggr1.remove((v6_1, v6_2, v6_elem))"
        # Begin maint _m_Aggr1_bbu after "Aggr1.add((v6_1, v6_2, v6_val))"
        _maint__m_Aggr1_bbu_add((v6_1, v6_2, v6_val))
        # End maint _m_Aggr1_bbu after "Aggr1.add((v6_1, v6_2, v6_val))"

_U_Aggr1 = RCSet()
_UEXT_Aggr1 = Set()
def demand_Aggr1(x, L):
    "sum(DEMQUERY(Comp1, [L], setmatch(Comp1, 'bbu', (x, L))), None)"
    if ((x, L) not in _U_Aggr1):
        _U_Aggr1.add((x, L))
        # Begin maint Aggr1 after "_U_Aggr1.add((x, L))"
        v7_val = 0
        for v7_elem in (_m_Comp1_bbu[(x, L)] if ((x, L) in _m_Comp1_bbu) else set()):
            v7_val = (v7_val + v7_elem)
        (v7_1, v7_2) = (x, L)
        # Begin maint _m_Aggr1_bbu after "Aggr1.add((v7_1, v7_2, v7_val))"
        _maint__m_Aggr1_bbu_add((v7_1, v7_2, v7_val))
        # End maint _m_Aggr1_bbu after "Aggr1.add((v7_1, v7_2, v7_val))"
        demand_Comp1(L)
        # End maint Aggr1 after "_U_Aggr1.add((x, L))"
    else:
        _U_Aggr1.incref((x, L))

def undemand_Aggr1(x, L):
    "sum(DEMQUERY(Comp1, [L], setmatch(Comp1, 'bbu', (x, L))), None)"
    if (_U_Aggr1.getref((x, L)) == 1):
        # Begin maint Aggr1 before "_U_Aggr1.remove((x, L))"
        undemand_Comp1(L)
        (v8_1, v8_2) = (x, L)
        v8_elem = _m_Aggr1_bbu.singlelookup((x, L))
        # Begin maint _m_Aggr1_bbu before "Aggr1.remove((v8_1, v8_2, v8_elem))"
        _maint__m_Aggr1_bbu_remove((v8_1, v8_2, v8_elem))
        # End maint _m_Aggr1_bbu before "Aggr1.remove((v8_1, v8_2, v8_elem))"
        # End maint Aggr1 before "_U_Aggr1.remove((x, L))"
        _U_Aggr1.remove((x, L))
    else:
        _U_Aggr1.decref((x, L))

def query_Aggr1(x, L):
    "sum(DEMQUERY(Comp1, [L], setmatch(Comp1, 'bbu', (x, L))), None)"
    if ((x, L) not in _UEXT_Aggr1):
        _UEXT_Aggr1.add((x, L))
        demand_Aggr1(x, L)
    return True

def _maint_Comp1__U_Comp1_add(_e):
    # Iterate {(v1_L, v1_x, v1_y) : v1_L in deltamatch(_U_Comp1, 'b', _e, 1), (v1_x, v1_y) in E, (v1_y < v1_L)}
    v1_L = _e
    for (v1_x, v1_y) in E:
        if (v1_y < v1_L):
            # Begin maint _m_Comp1_bbu after "Comp1.add((v1_x, v1_L, v1_y))"
            _maint__m_Comp1_bbu_add((v1_x, v1_L, v1_y))
            # End maint _m_Comp1_bbu after "Comp1.add((v1_x, v1_L, v1_y))"
            # Begin maint Aggr1 after "Comp1.add((v1_x, v1_L, v1_y))"
            _maint_Aggr1_add((v1_x, v1_L, v1_y))
            # End maint Aggr1 after "Comp1.add((v1_x, v1_L, v1_y))"

def _maint_Comp1__U_Comp1_remove(_e):
    # Iterate {(v2_L, v2_x, v2_y) : v2_L in deltamatch(_U_Comp1, 'b', _e, 1), (v2_x, v2_y) in E, (v2_y < v2_L)}
    v2_L = _e
    for (v2_x, v2_y) in E:
        if (v2_y < v2_L):
            # Begin maint Aggr1 before "Comp1.remove((v2_x, v2_L, v2_y))"
            _maint_Aggr1_remove((v2_x, v2_L, v2_y))
            # End maint Aggr1 before "Comp1.remove((v2_x, v2_L, v2_y))"
            # Begin maint _m_Comp1_bbu before "Comp1.remove((v2_x, v2_L, v2_y))"
            _maint__m_Comp1_bbu_remove((v2_x, v2_L, v2_y))
            # End maint _m_Comp1_bbu before "Comp1.remove((v2_x, v2_L, v2_y))"

def _maint_Comp1_E_add(_e):
    # Iterate {(v3_L, v3_x, v3_y) : v3_L in _U_Comp1, (v3_x, v3_y) in deltamatch(E, 'bb', _e, 1), (v3_y < v3_L)}
    (v3_x, v3_y) = _e
    for v3_L in _U_Comp1:
        if (v3_y < v3_L):
            # Begin maint _m_Comp1_bbu after "Comp1.add((v3_x, v3_L, v3_y))"
            _maint__m_Comp1_bbu_add((v3_x, v3_L, v3_y))
            # End maint _m_Comp1_bbu after "Comp1.add((v3_x, v3_L, v3_y))"
            # Begin maint Aggr1 after "Comp1.add((v3_x, v3_L, v3_y))"
            _maint_Aggr1_add((v3_x, v3_L, v3_y))
            # End maint Aggr1 after "Comp1.add((v3_x, v3_L, v3_y))"

def _maint_Comp1_E_remove(_e):
    # Iterate {(v4_L, v4_x, v4_y) : v4_L in _U_Comp1, (v4_x, v4_y) in deltamatch(E, 'bb', _e, 1), (v4_y < v4_L)}
    (v4_x, v4_y) = _e
    for v4_L in _U_Comp1:
        if (v4_y < v4_L):
            # Begin maint Aggr1 before "Comp1.remove((v4_x, v4_L, v4_y))"
            _maint_Aggr1_remove((v4_x, v4_L, v4_y))
            # End maint Aggr1 before "Comp1.remove((v4_x, v4_L, v4_y))"
            # Begin maint _m_Comp1_bbu before "Comp1.remove((v4_x, v4_L, v4_y))"
            _maint__m_Comp1_bbu_remove((v4_x, v4_L, v4_y))
            # End maint _m_Comp1_bbu before "Comp1.remove((v4_x, v4_L, v4_y))"

_U_Comp1 = RCSet()
_UEXT_Comp1 = Set()
def demand_Comp1(L):
    '{(x, L, y) : L in _U_Comp1, (x, y) in E, (y < L)}'
    if (L not in _U_Comp1):
        _U_Comp1.add(L)
        # Begin maint Comp1 after "_U_Comp1.add(L)"
        _maint_Comp1__U_Comp1_add(L)
        # End maint Comp1 after "_U_Comp1.add(L)"
    else:
        _U_Comp1.incref(L)

def undemand_Comp1(L):
    '{(x, L, y) : L in _U_Comp1, (x, y) in E, (y < L)}'
    if (_U_Comp1.getref(L) == 1):
        # Begin maint Comp1 before "_U_Comp1.remove(L)"
        _maint_Comp1__U_Comp1_remove(L)
        # End maint Comp1 before "_U_Comp1.remove(L)"
        _U_Comp1.remove(L)
    else:
        _U_Comp1.decref(L)

def query_Comp1(L):
    '{(x, L, y) : L in _U_Comp1, (x, y) in E, (y < L)}'
    if (L not in _UEXT_Comp1):
        _UEXT_Comp1.add(L)
        demand_Comp1(L)
    return True

E = Set()
for e in [(1, 2), (1, 3), (1, 15), (2, 4)]:
    E.add(e)
    # Begin maint Comp1 after "E.add(e)"
    _maint_Comp1_E_add(e)
    # End maint Comp1 after "E.add(e)"
L = 10
x = 1
print((query_Aggr1(x, L) and _m_Aggr1_bbu.singlelookup((x, L))))
# Begin maint Comp1 before "E.remove((1, 3))"
_maint_Comp1_E_remove((1, 3))
# End maint Comp1 before "E.remove((1, 3))"
E.remove((1, 3))
print((query_Aggr1(x, L) and _m_Aggr1_bbu.singlelookup((x, L))))