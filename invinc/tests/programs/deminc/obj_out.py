from invinc.runtime import *
# Comp1 := {(S, x_a) : S in _U_Comp1, (S, x) in _M, (x, x_a) in _F_a}
# Comp1_TS := {S : S in _U_Comp1}
# Comp1_d_M := {(S, x) : S in Comp1_TS, (S, x) in _M}
# Comp1_Tx := {x : (S, x) in Comp1_d_M}
# Comp1_d_F_a := {(x, x_a) : x in Comp1_Tx, (x, x_a) in _F_a}
_m_Comp1_out = Map()
def _maint__m_Comp1_out_add(_e):
    (v21_1, v21_2) = _e
    if (v21_1 not in _m_Comp1_out):
        _m_Comp1_out[v21_1] = set()
    _m_Comp1_out[v21_1].add(v21_2)

def _maint__m_Comp1_out_remove(_e):
    (v22_1, v22_2) = _e
    _m_Comp1_out[v22_1].remove(v22_2)
    if (len(_m_Comp1_out[v22_1]) == 0):
        del _m_Comp1_out[v22_1]

_m_Comp1_d_M_in = Map()
def _maint__m_Comp1_d_M_in_add(_e):
    (v19_1, v19_2) = _e
    if (v19_2 not in _m_Comp1_d_M_in):
        _m_Comp1_d_M_in[v19_2] = set()
    _m_Comp1_d_M_in[v19_2].add(v19_1)

def _maint__m_Comp1_d_M_in_remove(_e):
    (v20_1, v20_2) = _e
    _m_Comp1_d_M_in[v20_2].remove(v20_1)
    if (len(_m_Comp1_d_M_in[v20_2]) == 0):
        del _m_Comp1_d_M_in[v20_2]

Comp1_d_F_a = RCSet()
def _maint_Comp1_d_F_a_Comp1_Tx_add(_e):
    # Iterate {(v15_x, v15_x_a) : v15_x in deltamatch(Comp1_Tx, 'b', _e, 1), (v15_x, v15_x_a) in _F_a}
    v15_x = _e
    if hasattr(v15_x, 'a'):
        v15_x_a = v15_x.a
        Comp1_d_F_a.add((v15_x, v15_x_a))

def _maint_Comp1_d_F_a_Comp1_Tx_remove(_e):
    # Iterate {(v16_x, v16_x_a) : v16_x in deltamatch(Comp1_Tx, 'b', _e, 1), (v16_x, v16_x_a) in _F_a}
    v16_x = _e
    if hasattr(v16_x, 'a'):
        v16_x_a = v16_x.a
        Comp1_d_F_a.remove((v16_x, v16_x_a))

def _maint_Comp1_d_F_a__F_a_add(_e):
    # Iterate {(v17_x, v17_x_a) : v17_x in Comp1_Tx, (v17_x, v17_x_a) in deltamatch(_F_a, 'bb', _e, 1)}
    (v17_x, v17_x_a) = _e
    if (v17_x in Comp1_Tx):
        Comp1_d_F_a.add((v17_x, v17_x_a))

Comp1_Tx = RCSet()
def _maint_Comp1_Tx_Comp1_d_M_add(_e):
    # Iterate {(v13_S, v13_x) : (v13_S, v13_x) in deltamatch(Comp1_d_M, 'bb', _e, 1)}
    (v13_S, v13_x) = _e
    if (v13_x not in Comp1_Tx):
        Comp1_Tx.add(v13_x)
        # Begin maint Comp1_d_F_a after "Comp1_Tx.add(v13_x)"
        _maint_Comp1_d_F_a_Comp1_Tx_add(v13_x)
        # End maint Comp1_d_F_a after "Comp1_Tx.add(v13_x)"
    else:
        Comp1_Tx.incref(v13_x)

def _maint_Comp1_Tx_Comp1_d_M_remove(_e):
    # Iterate {(v14_S, v14_x) : (v14_S, v14_x) in deltamatch(Comp1_d_M, 'bb', _e, 1)}
    (v14_S, v14_x) = _e
    if (Comp1_Tx.getref(v14_x) == 1):
        # Begin maint Comp1_d_F_a before "Comp1_Tx.remove(v14_x)"
        _maint_Comp1_d_F_a_Comp1_Tx_remove(v14_x)
        # End maint Comp1_d_F_a before "Comp1_Tx.remove(v14_x)"
        Comp1_Tx.remove(v14_x)
    else:
        Comp1_Tx.decref(v14_x)

Comp1_d_M = RCSet()
def _maint_Comp1_d_M_Comp1_TS_add(_e):
    # Iterate {(v9_S, v9_x) : v9_S in deltamatch(Comp1_TS, 'b', _e, 1), (v9_S, v9_x) in _M}
    v9_S = _e
    if isinstance(v9_S, Set):
        for v9_x in v9_S:
            Comp1_d_M.add((v9_S, v9_x))
            # Begin maint _m_Comp1_d_M_in after "Comp1_d_M.add((v9_S, v9_x))"
            _maint__m_Comp1_d_M_in_add((v9_S, v9_x))
            # End maint _m_Comp1_d_M_in after "Comp1_d_M.add((v9_S, v9_x))"
            # Begin maint Comp1_Tx after "Comp1_d_M.add((v9_S, v9_x))"
            _maint_Comp1_Tx_Comp1_d_M_add((v9_S, v9_x))
            # End maint Comp1_Tx after "Comp1_d_M.add((v9_S, v9_x))"

def _maint_Comp1_d_M_Comp1_TS_remove(_e):
    # Iterate {(v10_S, v10_x) : v10_S in deltamatch(Comp1_TS, 'b', _e, 1), (v10_S, v10_x) in _M}
    v10_S = _e
    if isinstance(v10_S, Set):
        for v10_x in v10_S:
            # Begin maint Comp1_Tx before "Comp1_d_M.remove((v10_S, v10_x))"
            _maint_Comp1_Tx_Comp1_d_M_remove((v10_S, v10_x))
            # End maint Comp1_Tx before "Comp1_d_M.remove((v10_S, v10_x))"
            # Begin maint _m_Comp1_d_M_in before "Comp1_d_M.remove((v10_S, v10_x))"
            _maint__m_Comp1_d_M_in_remove((v10_S, v10_x))
            # End maint _m_Comp1_d_M_in before "Comp1_d_M.remove((v10_S, v10_x))"
            Comp1_d_M.remove((v10_S, v10_x))

def _maint_Comp1_d_M__M_add(_e):
    # Iterate {(v11_S, v11_x) : v11_S in Comp1_TS, (v11_S, v11_x) in deltamatch(_M, 'bb', _e, 1)}
    (v11_S, v11_x) = _e
    if (v11_S in Comp1_TS):
        Comp1_d_M.add((v11_S, v11_x))
        # Begin maint _m_Comp1_d_M_in after "Comp1_d_M.add((v11_S, v11_x))"
        _maint__m_Comp1_d_M_in_add((v11_S, v11_x))
        # End maint _m_Comp1_d_M_in after "Comp1_d_M.add((v11_S, v11_x))"
        # Begin maint Comp1_Tx after "Comp1_d_M.add((v11_S, v11_x))"
        _maint_Comp1_Tx_Comp1_d_M_add((v11_S, v11_x))
        # End maint Comp1_Tx after "Comp1_d_M.add((v11_S, v11_x))"

Comp1_TS = RCSet()
def _maint_Comp1_TS__U_Comp1_add(_e):
    # Iterate {v7_S : v7_S in deltamatch(_U_Comp1, 'b', _e, 1)}
    v7_S = _e
    Comp1_TS.add(v7_S)
    # Begin maint Comp1_d_M after "Comp1_TS.add(v7_S)"
    _maint_Comp1_d_M_Comp1_TS_add(v7_S)
    # End maint Comp1_d_M after "Comp1_TS.add(v7_S)"

def _maint_Comp1_TS__U_Comp1_remove(_e):
    # Iterate {v8_S : v8_S in deltamatch(_U_Comp1, 'b', _e, 1)}
    v8_S = _e
    # Begin maint Comp1_d_M before "Comp1_TS.remove(v8_S)"
    _maint_Comp1_d_M_Comp1_TS_remove(v8_S)
    # End maint Comp1_d_M before "Comp1_TS.remove(v8_S)"
    Comp1_TS.remove(v8_S)

Comp1 = RCSet()
def _maint_Comp1__U_Comp1_add(_e):
    # Iterate {(v1_S, v1_x, v1_x_a) : v1_S in deltamatch(_U_Comp1, 'b', _e, 1), (v1_S, v1_x) in _M, (v1_x, v1_x_a) in _F_a}
    v1_S = _e
    if isinstance(v1_S, Set):
        for v1_x in v1_S:
            if hasattr(v1_x, 'a'):
                v1_x_a = v1_x.a
                if ((v1_S, v1_x_a) not in Comp1):
                    Comp1.add((v1_S, v1_x_a))
                    # Begin maint _m_Comp1_out after "Comp1.add((v1_S, v1_x_a))"
                    _maint__m_Comp1_out_add((v1_S, v1_x_a))
                    # End maint _m_Comp1_out after "Comp1.add((v1_S, v1_x_a))"
                else:
                    Comp1.incref((v1_S, v1_x_a))

def _maint_Comp1__U_Comp1_remove(_e):
    # Iterate {(v2_S, v2_x, v2_x_a) : v2_S in deltamatch(_U_Comp1, 'b', _e, 1), (v2_S, v2_x) in _M, (v2_x, v2_x_a) in _F_a}
    v2_S = _e
    if isinstance(v2_S, Set):
        for v2_x in v2_S:
            if hasattr(v2_x, 'a'):
                v2_x_a = v2_x.a
                if (Comp1.getref((v2_S, v2_x_a)) == 1):
                    # Begin maint _m_Comp1_out before "Comp1.remove((v2_S, v2_x_a))"
                    _maint__m_Comp1_out_remove((v2_S, v2_x_a))
                    # End maint _m_Comp1_out before "Comp1.remove((v2_S, v2_x_a))"
                    Comp1.remove((v2_S, v2_x_a))
                else:
                    Comp1.decref((v2_S, v2_x_a))

def _maint_Comp1__M_add(_e):
    # Iterate {(v3_S, v3_x, v3_x_a) : v3_S in _U_Comp1, (v3_S, v3_x) in deltamatch(Comp1_d_M, 'bb', _e, 1), (v3_S, v3_x) in Comp1_d_M, (v3_x, v3_x_a) in _F_a}
    (v3_S, v3_x) = _e
    if (v3_S in _U_Comp1):
        if ((v3_S, v3_x) in Comp1_d_M):
            if hasattr(v3_x, 'a'):
                v3_x_a = v3_x.a
                if ((v3_S, v3_x_a) not in Comp1):
                    Comp1.add((v3_S, v3_x_a))
                    # Begin maint _m_Comp1_out after "Comp1.add((v3_S, v3_x_a))"
                    _maint__m_Comp1_out_add((v3_S, v3_x_a))
                    # End maint _m_Comp1_out after "Comp1.add((v3_S, v3_x_a))"
                else:
                    Comp1.incref((v3_S, v3_x_a))

def _maint_Comp1__F_a_add(_e):
    # Iterate {(v5_S, v5_x, v5_x_a) : v5_S in _U_Comp1, (v5_S, v5_x) in Comp1_d_M, (v5_x, v5_x_a) in deltamatch(Comp1_d_F_a, 'bb', _e, 1), (v5_x, v5_x_a) in Comp1_d_F_a}
    (v5_x, v5_x_a) = _e
    if ((v5_x, v5_x_a) in Comp1_d_F_a):
        for v5_S in (_m_Comp1_d_M_in[v5_x] if (v5_x in _m_Comp1_d_M_in) else set()):
            if (v5_S in _U_Comp1):
                if ((v5_S, v5_x_a) not in Comp1):
                    Comp1.add((v5_S, v5_x_a))
                    # Begin maint _m_Comp1_out after "Comp1.add((v5_S, v5_x_a))"
                    _maint__m_Comp1_out_add((v5_S, v5_x_a))
                    # End maint _m_Comp1_out after "Comp1.add((v5_S, v5_x_a))"
                else:
                    Comp1.incref((v5_S, v5_x_a))

_U_Comp1 = RCSet()
_UEXT_Comp1 = Set()
def demand_Comp1(S):
    '{(S, x_a) : S in _U_Comp1, (S, x) in _M, (x, x_a) in _F_a}'
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
    '{(S, x_a) : S in _U_Comp1, (S, x) in _M, (x, x_a) in _F_a}'
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
    '{(S, x_a) : S in _U_Comp1, (S, x) in _M, (x, x_a) in _F_a}'
    if (S not in _UEXT_Comp1):
        _UEXT_Comp1.add(S)
        demand_Comp1(S)
    return True

S = Set()
o = Obj()
o.a = 1
# Begin maint Comp1_d_F_a after "_F_a.add((o, 1))"
_maint_Comp1_d_F_a__F_a_add((o, 1))
# End maint Comp1_d_F_a after "_F_a.add((o, 1))"
# Begin maint Comp1 after "_F_a.add((o, 1))"
_maint_Comp1__F_a_add((o, 1))
# End maint Comp1 after "_F_a.add((o, 1))"
S.add(o)
# Begin maint Comp1_d_M after "_M.add((S, o))"
_maint_Comp1_d_M__M_add((S, o))
# End maint Comp1_d_M after "_M.add((S, o))"
# Begin maint Comp1 after "_M.add((S, o))"
_maint_Comp1__M_add((S, o))
# End maint Comp1 after "_M.add((S, o))"
print(sorted((query_Comp1(S) and (_m_Comp1_out[S] if (S in _m_Comp1_out) else set()))))