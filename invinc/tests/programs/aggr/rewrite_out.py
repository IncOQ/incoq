from invinc.runtime import *
# Comp1 := {(R, _e) : R in _U_Comp1, (R, _e) in _M}
# Aggr1 := sum(DEMQUERY(Comp1, [R], setmatch(Comp1, 'bu', R)), None)
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
_UEXT_Aggr1 = Set()
def demand_Aggr1(R):
    "sum(DEMQUERY(Comp1, [R], setmatch(Comp1, 'bu', R)), None)"
    if (R not in _U_Aggr1):
        _U_Aggr1.add(R)
        # Begin maint Aggr1 after "_U_Aggr1.add(R)"
        v7_val = 0
        for v7_elem in (_m_Comp1_out[R] if (R in _m_Comp1_out) else set()):
            v7_val = (v7_val + v7_elem)
        v7_1 = R
        # Begin maint _m_Aggr1_out after "Aggr1.add((v7_1, v7_val))"
        _maint__m_Aggr1_out_add((v7_1, v7_val))
        # End maint _m_Aggr1_out after "Aggr1.add((v7_1, v7_val))"
        demand_Comp1(R)
        # End maint Aggr1 after "_U_Aggr1.add(R)"
    else:
        _U_Aggr1.incref(R)

def undemand_Aggr1(R):
    "sum(DEMQUERY(Comp1, [R], setmatch(Comp1, 'bu', R)), None)"
    if (_U_Aggr1.getref(R) == 1):
        # Begin maint Aggr1 before "_U_Aggr1.remove(R)"
        undemand_Comp1(R)
        v8_1 = R
        v8_elem = _m_Aggr1_out.singlelookup(R)
        # Begin maint _m_Aggr1_out before "Aggr1.remove((v8_1, v8_elem))"
        _maint__m_Aggr1_out_remove((v8_1, v8_elem))
        # End maint _m_Aggr1_out before "Aggr1.remove((v8_1, v8_elem))"
        # End maint Aggr1 before "_U_Aggr1.remove(R)"
        _U_Aggr1.remove(R)
    else:
        _U_Aggr1.decref(R)

def query_Aggr1(R):
    "sum(DEMQUERY(Comp1, [R], setmatch(Comp1, 'bu', R)), None)"
    if (R not in _UEXT_Aggr1):
        _UEXT_Aggr1.add(R)
        demand_Aggr1(R)
    return True

def _maint_Comp1__U_Comp1_add(_e):
    # Iterate {(v1_R, v1__e) : v1_R in deltamatch(_U_Comp1, 'b', _e, 1), (v1_R, v1__e) in _M}
    v1_R = _e
    if isinstance(v1_R, Set):
        for v1__e in v1_R:
            # Begin maint _m_Comp1_out after "Comp1.add((v1_R, v1__e))"
            _maint__m_Comp1_out_add((v1_R, v1__e))
            # End maint _m_Comp1_out after "Comp1.add((v1_R, v1__e))"
            # Begin maint Aggr1 after "Comp1.add((v1_R, v1__e))"
            _maint_Aggr1_add((v1_R, v1__e))
            # End maint Aggr1 after "Comp1.add((v1_R, v1__e))"

def _maint_Comp1__U_Comp1_remove(_e):
    # Iterate {(v2_R, v2__e) : v2_R in deltamatch(_U_Comp1, 'b', _e, 1), (v2_R, v2__e) in _M}
    v2_R = _e
    if isinstance(v2_R, Set):
        for v2__e in v2_R:
            # Begin maint Aggr1 before "Comp1.remove((v2_R, v2__e))"
            _maint_Aggr1_remove((v2_R, v2__e))
            # End maint Aggr1 before "Comp1.remove((v2_R, v2__e))"
            # Begin maint _m_Comp1_out before "Comp1.remove((v2_R, v2__e))"
            _maint__m_Comp1_out_remove((v2_R, v2__e))
            # End maint _m_Comp1_out before "Comp1.remove((v2_R, v2__e))"

def _maint_Comp1__M_add(_e):
    # Iterate {(v3_R, v3__e) : v3_R in _U_Comp1, (v3_R, v3__e) in deltamatch(_M, 'bb', _e, 1)}
    (v3_R, v3__e) = _e
    if (v3_R in _U_Comp1):
        # Begin maint _m_Comp1_out after "Comp1.add((v3_R, v3__e))"
        _maint__m_Comp1_out_add((v3_R, v3__e))
        # End maint _m_Comp1_out after "Comp1.add((v3_R, v3__e))"
        # Begin maint Aggr1 after "Comp1.add((v3_R, v3__e))"
        _maint_Aggr1_add((v3_R, v3__e))
        # End maint Aggr1 after "Comp1.add((v3_R, v3__e))"

_U_Comp1 = RCSet()
_UEXT_Comp1 = Set()
def demand_Comp1(R):
    '{(R, _e) : R in _U_Comp1, (R, _e) in _M}'
    if (R not in _U_Comp1):
        _U_Comp1.add(R)
        # Begin maint Comp1 after "_U_Comp1.add(R)"
        _maint_Comp1__U_Comp1_add(R)
        # End maint Comp1 after "_U_Comp1.add(R)"
    else:
        _U_Comp1.incref(R)

def undemand_Comp1(R):
    '{(R, _e) : R in _U_Comp1, (R, _e) in _M}'
    if (_U_Comp1.getref(R) == 1):
        # Begin maint Comp1 before "_U_Comp1.remove(R)"
        _maint_Comp1__U_Comp1_remove(R)
        # End maint Comp1 before "_U_Comp1.remove(R)"
        _U_Comp1.remove(R)
    else:
        _U_Comp1.decref(R)

def query_Comp1(R):
    '{(R, _e) : R in _U_Comp1, (R, _e) in _M}'
    if (R not in _UEXT_Comp1):
        _UEXT_Comp1.add(R)
        demand_Comp1(R)
    return True

R = Set()
R.add(1)
# Begin maint Comp1 after "_M.add((R, 1))"
_maint_Comp1__M_add((R, 1))
# End maint Comp1 after "_M.add((R, 1))"
print((query_Aggr1(R) and _m_Aggr1_out.singlelookup(R)))
print(sum({1, 2}))
print(sum([1, 2]))
print(sum(({1: 1}[1], 2)))