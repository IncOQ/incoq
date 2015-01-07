from oinc.runtime import *
# Aggr1 := sum(R, None)
# Comp1 := {x : x in S, _av1 in {Aggr1.smlookup('u', (), None)}, (x > _av1)}
# Aggr1_delta := {() : _ in S}
_m_R_u = Map()
def _maint__m_R_u_add(_e):
    v16_1 = _e
    if (() not in _m_R_u):
        _m_R_u[()] = set()
    _m_R_u[()].add(v16_1)

def _maint__m_R_u_remove(_e):
    v17_1 = _e
    _m_R_u[()].remove(v17_1)
    if (len(_m_R_u[()]) == 0):
        del _m_R_u[()]

_m_Aggr1_u = Map()
def _maint__m_Aggr1_u_add(_e):
    v14_1 = _e
    if (() not in _m_Aggr1_u):
        _m_Aggr1_u[()] = set()
    _m_Aggr1_u[()].add(v14_1)

def _maint__m_Aggr1_u_remove(_e):
    v15_1 = _e
    _m_Aggr1_u[()].remove(v15_1)
    if (len(_m_Aggr1_u[()]) == 0):
        del _m_Aggr1_u[()]

_m_S_w = Map()
def _maint__m_S_w_add(_e):
    if (() not in _m_S_w):
        _m_S_w[()] = RCSet()
    if (() not in _m_S_w[()]):
        _m_S_w[()].add(())
    else:
        _m_S_w[()].incref(())

Aggr1_delta = RCSet()
def _maint_Aggr1_delta_S_add(_e):
    # Iterate {() : _ in deltamatch(S, 'w', _e, 1)}
    for _ in setmatch(({_e} if ((_m_S_w[()] if (() in _m_S_w) else RCSet()).getref(()) == 1) else {}), 'w', ()):
        Aggr1_delta.add(())

Comp1 = RCSet()
def _maint_Comp1_S_add(_e):
    # Iterate {(v5_x, v5__av1) : v5_x in deltamatch(S, 'b', _e, 1), v5__av1 in {Aggr1.smlookup('u', (), None)}, (v5_x > v5__av1)}
    v5_x = _e
    for v5__av1 in Aggr1:
        if (v5_x > v5__av1):
            if (v5_x not in Comp1):
                Comp1.add(v5_x)
            else:
                Comp1.incref(v5_x)

def _maint_Comp1_Aggr1_add(_e):
    # Iterate {(v7_x, v7__av1) : v7_x in S, v7__av1 in deltamatch(Aggr1, 'b', _e, 1), (v7_x > v7__av1)}
    v7__av1 = _e
    for v7_x in S:
        if (v7_x > v7__av1):
            if (v7_x not in Comp1):
                Comp1.add(v7_x)
            else:
                Comp1.incref(v7_x)

def _maint_Comp1_Aggr1_remove(_e):
    # Iterate {(v8_x, v8__av1) : v8_x in S, v8__av1 in deltamatch(Aggr1, 'b', _e, 1), (v8_x > v8__av1)}
    v8__av1 = _e
    for v8_x in S:
        if (v8_x > v8__av1):
            if (Comp1.getref(v8_x) == 1):
                Comp1.remove(v8_x)
            else:
                Comp1.decref(v8_x)

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

def _maint_Aggr1_remove(_e):
    v2_v1 = _e
    if (() in _U_Aggr1):
        v2_val = _m_Aggr1_u.singlelookup(())
        v2_val = (v2_val - v2_v1)
        v2_elem = _m_Aggr1_u.singlelookup(())
        # Begin maint Comp1 before "Aggr1.remove(v2_elem)"
        _maint_Comp1_Aggr1_remove(v2_elem)
        # End maint Comp1 before "Aggr1.remove(v2_elem)"
        # Begin maint _m_Aggr1_u before "Aggr1.remove(v2_elem)"
        _maint__m_Aggr1_u_remove(v2_elem)
        # End maint _m_Aggr1_u before "Aggr1.remove(v2_elem)"
        Aggr1.remove(v2_elem)
        Aggr1.add(v2_val)
        # Begin maint _m_Aggr1_u after "Aggr1.add(v2_val)"
        _maint__m_Aggr1_u_add(v2_val)
        # End maint _m_Aggr1_u after "Aggr1.add(v2_val)"
        # Begin maint Comp1 after "Aggr1.add(v2_val)"
        _maint_Comp1_Aggr1_add(v2_val)
        # End maint Comp1 after "Aggr1.add(v2_val)"

_U_Aggr1 = RCSet()
_UEXT_Aggr1 = Set()
def demand_Aggr1():
    'sum(R, None)'
    if (() not in _U_Aggr1):
        _U_Aggr1.add(())
        # Begin maint Aggr1 after "_U_Aggr1.add(())"
        v3_val = 0
        for v3_elem in (_m_R_u[()] if (() in _m_R_u) else set()):
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
    'sum(R, None)'
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
    'sum(R, None)'
    if (() not in _UEXT_Aggr1):
        _UEXT_Aggr1.add(())
        demand_Aggr1()
    return True

S = Set()
for e in [1, 5, 15, 20]:
    S.add(e)
    # Begin maint _m_S_w after "S.add(e)"
    _maint__m_S_w_add(e)
    # End maint _m_S_w after "S.add(e)"
    # Begin maint Aggr1_delta after "S.add(e)"
    _maint_Aggr1_delta_S_add(e)
    # End maint Aggr1_delta after "S.add(e)"
    # Begin maint Comp1 after "S.add(e)"
    _maint_Comp1_S_add(e)
    # End maint Comp1 after "S.add(e)"
    # Begin maint demand_Aggr1 after "S.add(e)"
    for _ in Aggr1_delta.elements():
        demand_Aggr1()
    Aggr1_delta.clear()
    # End maint demand_Aggr1 after "S.add(e)"
for e in [1, 2, 3, 4]:
    # Begin maint _m_R_u after "R.add(e)"
    _maint__m_R_u_add(e)
    # End maint _m_R_u after "R.add(e)"
    # Begin maint Aggr1 after "R.add(e)"
    _maint_Aggr1_add(e)
    # End maint Aggr1 after "R.add(e)"
print(sorted(Comp1))
for e in [1, 2, 3, 4]:
    # Begin maint Aggr1 before "R.remove(e)"
    _maint_Aggr1_remove(e)
    # End maint Aggr1 before "R.remove(e)"
    # Begin maint _m_R_u before "R.remove(e)"
    _maint__m_R_u_remove(e)
    # End maint _m_R_u before "R.remove(e)"
print(sorted(Comp1))