from incoq.runtime import *
# Comp1 := {(S, S) : S in _U_Comp1, (S, _) in _M}
# Comp1_TS := {S : S in _U_Comp1}
# Comp1_d_M := {(S, _v1) : S in Comp1_TS, (S, _v1) in _M}
_m_Comp1_out = Map()
def _maint__m_Comp1_out_add(_e):
    (v13_1, v13_2) = _e
    if (v13_1 not in _m_Comp1_out):
        _m_Comp1_out[v13_1] = set()
    _m_Comp1_out[v13_1].add(v13_2)

def _maint__m_Comp1_out_remove(_e):
    (v14_1, v14_2) = _e
    _m_Comp1_out[v14_1].remove(v14_2)
    if (len(_m_Comp1_out[v14_1]) == 0):
        del _m_Comp1_out[v14_1]

_m_Comp1_d_M_bw = Map()
def _maint__m_Comp1_d_M_bw_add(_e):
    (v11_1, v11_2) = _e
    if (v11_1 not in _m_Comp1_d_M_bw):
        _m_Comp1_d_M_bw[v11_1] = RCSet()
    if (() not in _m_Comp1_d_M_bw[v11_1]):
        _m_Comp1_d_M_bw[v11_1].add(())
    else:
        _m_Comp1_d_M_bw[v11_1].incref(())

def _maint__m_Comp1_d_M_bw_remove(_e):
    (v12_1, v12_2) = _e
    if (_m_Comp1_d_M_bw[v12_1].getref(()) == 1):
        _m_Comp1_d_M_bw[v12_1].remove(())
    else:
        _m_Comp1_d_M_bw[v12_1].decref(())
    if (len(_m_Comp1_d_M_bw[v12_1]) == 0):
        del _m_Comp1_d_M_bw[v12_1]

def _maint_Comp1_d_M_Comp1_TS_add(_e):
    # Iterate {(v7_S, v7__v1) : v7_S in deltamatch(Comp1_TS, 'b', _e, 1), (v7_S, v7__v1) in _M}
    v7_S = _e
    if isinstance(v7_S, Set):
        for v7__v1 in v7_S:
            # Begin maint _m_Comp1_d_M_bw after "Comp1_d_M.add((v7_S, v7__v1))"
            _maint__m_Comp1_d_M_bw_add((v7_S, v7__v1))
            # End maint _m_Comp1_d_M_bw after "Comp1_d_M.add((v7_S, v7__v1))"

def _maint_Comp1_d_M_Comp1_TS_remove(_e):
    # Iterate {(v8_S, v8__v1) : v8_S in deltamatch(Comp1_TS, 'b', _e, 1), (v8_S, v8__v1) in _M}
    v8_S = _e
    if isinstance(v8_S, Set):
        for v8__v1 in v8_S:
            # Begin maint _m_Comp1_d_M_bw before "Comp1_d_M.remove((v8_S, v8__v1))"
            _maint__m_Comp1_d_M_bw_remove((v8_S, v8__v1))
            # End maint _m_Comp1_d_M_bw before "Comp1_d_M.remove((v8_S, v8__v1))"

def _maint_Comp1_d_M__M_add(_e):
    # Iterate {(v9_S, v9__v1) : v9_S in Comp1_TS, (v9_S, v9__v1) in deltamatch(_M, 'bb', _e, 1)}
    (v9_S, v9__v1) = _e
    if (v9_S in Comp1_TS):
        # Begin maint _m_Comp1_d_M_bw after "Comp1_d_M.add((v9_S, v9__v1))"
        _maint__m_Comp1_d_M_bw_add((v9_S, v9__v1))
        # End maint _m_Comp1_d_M_bw after "Comp1_d_M.add((v9_S, v9__v1))"

Comp1_TS = RCSet()
def _maint_Comp1_TS__U_Comp1_add(_e):
    # Iterate {v5_S : v5_S in deltamatch(_U_Comp1, 'b', _e, 1)}
    v5_S = _e
    Comp1_TS.add(v5_S)
    # Begin maint Comp1_d_M after "Comp1_TS.add(v5_S)"
    _maint_Comp1_d_M_Comp1_TS_add(v5_S)
    # End maint Comp1_d_M after "Comp1_TS.add(v5_S)"

def _maint_Comp1_TS__U_Comp1_remove(_e):
    # Iterate {v6_S : v6_S in deltamatch(_U_Comp1, 'b', _e, 1)}
    v6_S = _e
    # Begin maint Comp1_d_M before "Comp1_TS.remove(v6_S)"
    _maint_Comp1_d_M_Comp1_TS_remove(v6_S)
    # End maint Comp1_d_M before "Comp1_TS.remove(v6_S)"
    Comp1_TS.remove(v6_S)

def _maint_Comp1__U_Comp1_add(_e):
    # Iterate {v1_S : v1_S in deltamatch(_U_Comp1, 'b', _e, 1), (v1_S, _) in _M}
    v1_S = _e
    if isinstance(v1_S, Set):
        if (not (len(v1_S) == 0)):
            # Begin maint _m_Comp1_out after "Comp1.add((v1_S, v1_S))"
            _maint__m_Comp1_out_add((v1_S, v1_S))
            # End maint _m_Comp1_out after "Comp1.add((v1_S, v1_S))"

def _maint_Comp1__U_Comp1_remove(_e):
    # Iterate {v2_S : v2_S in deltamatch(_U_Comp1, 'b', _e, 1), (v2_S, _) in _M}
    v2_S = _e
    if isinstance(v2_S, Set):
        if (not (len(v2_S) == 0)):
            # Begin maint _m_Comp1_out before "Comp1.remove((v2_S, v2_S))"
            _maint__m_Comp1_out_remove((v2_S, v2_S))
            # End maint _m_Comp1_out before "Comp1.remove((v2_S, v2_S))"

def _maint_Comp1__M_add(_e):
    # Iterate {v3_S : v3_S in _U_Comp1, (v3_S, _) in deltamatch(Comp1_d_M, 'bw', _e, 1), (v3_S, _) in Comp1_d_M}
    for v3_S in setmatch(({_e} if ((_m_Comp1_d_M_bw[_e[0]] if (_e[0] in _m_Comp1_d_M_bw) else RCSet()).getref(()) == 1) else {}), 'uw', ()):
        if (v3_S in _U_Comp1):
            for _ in (_m_Comp1_d_M_bw[v3_S] if (v3_S in _m_Comp1_d_M_bw) else RCSet()):
                # Begin maint _m_Comp1_out after "Comp1.add((v3_S, v3_S))"
                _maint__m_Comp1_out_add((v3_S, v3_S))
                # End maint _m_Comp1_out after "Comp1.add((v3_S, v3_S))"

_U_Comp1 = RCSet()
_UEXT_Comp1 = Set()
def demand_Comp1(S):
    '{(S, S) : S in _U_Comp1, (S, _) in _M}'
    if (S not in _U_Comp1):
        _U_Comp1.add(S)
        # Begin maint Comp1_TS after "_U_Comp1.add(S)"
        _maint_Comp1_TS__U_Comp1_add(S)
        # End maint Comp1_TS after "_U_Comp1.add(S)"
        # Begin maint Comp1 after "_U_Comp1.add(S)"
        _maint_Comp1__U_Comp1_add(S)
        # End maint Comp1 after "_U_Comp1.add(S)"
    else:
        _U_Comp1.incref(S)

def undemand_Comp1(S):
    '{(S, S) : S in _U_Comp1, (S, _) in _M}'
    if (_U_Comp1.getref(S) == 1):
        # Begin maint Comp1 before "_U_Comp1.remove(S)"
        _maint_Comp1__U_Comp1_remove(S)
        # End maint Comp1 before "_U_Comp1.remove(S)"
        # Begin maint Comp1_TS before "_U_Comp1.remove(S)"
        _maint_Comp1_TS__U_Comp1_remove(S)
        # End maint Comp1_TS before "_U_Comp1.remove(S)"
        _U_Comp1.remove(S)
    else:
        _U_Comp1.decref(S)

def query_Comp1(S):
    '{(S, S) : S in _U_Comp1, (S, _) in _M}'
    if (S not in _UEXT_Comp1):
        _UEXT_Comp1.add(S)
        demand_Comp1(S)
    return True

S = Set()
o = Obj()
o.a = 1
S.add(o)
# Begin maint Comp1_d_M after "_M.add((S, o))"
_maint_Comp1_d_M__M_add((S, o))
# End maint Comp1_d_M after "_M.add((S, o))"
# Begin maint Comp1 after "_M.add((S, o))"
_maint_Comp1__M_add((S, o))
# End maint Comp1 after "_M.add((S, o))"
print(len_((query_Comp1(S) and (_m_Comp1_out[S] if (S in _m_Comp1_out) else set()))))