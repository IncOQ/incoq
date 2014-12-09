from runtimelib import *
# Comp1 := {(s, a) : s in _U_Comp1, (s, _tup1) in _M, (_tup1, a, _) in _TUP2, (a > 1)}
# Comp1_Ts := {s : s in _U_Comp1}
# Comp1_d_M := {(s, _tup1) : s in Comp1_Ts, (s, _tup1) in _M}
# Comp1_T_tup1 := {_tup1 : (s, _tup1) in Comp1_d_M}
# Comp1_d_TUP2 := {(_tup1, a, _v1) : _tup1 in Comp1_T_tup1, (_tup1, a, _v1) in _TUP2}
_m_Comp1_out = Map()
def _maint__m_Comp1_out_add(_e):
    (v23_1, v23_2) = _e
    if (v23_1 not in _m_Comp1_out):
        _m_Comp1_out[v23_1] = set()
    _m_Comp1_out[v23_1].add(v23_2)

def _maint__m_Comp1_out_remove(_e):
    (v24_1, v24_2) = _e
    _m_Comp1_out[v24_1].remove(v24_2)
    if (len(_m_Comp1_out[v24_1]) == 0):
        del _m_Comp1_out[v24_1]

_m_Comp1_d_M_in = Map()
def _maint__m_Comp1_d_M_in_add(_e):
    (v21_1, v21_2) = _e
    if (v21_2 not in _m_Comp1_d_M_in):
        _m_Comp1_d_M_in[v21_2] = set()
    _m_Comp1_d_M_in[v21_2].add(v21_1)

def _maint__m_Comp1_d_M_in_remove(_e):
    (v22_1, v22_2) = _e
    _m_Comp1_d_M_in[v22_2].remove(v22_1)
    if (len(_m_Comp1_d_M_in[v22_2]) == 0):
        del _m_Comp1_d_M_in[v22_2]

_m_Comp1_d_TUP2_bbw = Map()
def _maint__m_Comp1_d_TUP2_bbw_add(_e):
    (v19_1, v19_2, v19_3) = _e
    if ((v19_1, v19_2) not in _m_Comp1_d_TUP2_bbw):
        _m_Comp1_d_TUP2_bbw[(v19_1, v19_2)] = RCSet()
    if (() not in _m_Comp1_d_TUP2_bbw[(v19_1, v19_2)]):
        _m_Comp1_d_TUP2_bbw[(v19_1, v19_2)].add(())
    else:
        _m_Comp1_d_TUP2_bbw[(v19_1, v19_2)].incref(())

def _maint__m_Comp1_d_TUP2_bbw_remove(_e):
    (v20_1, v20_2, v20_3) = _e
    if (_m_Comp1_d_TUP2_bbw[(v20_1, v20_2)].getref(()) == 1):
        _m_Comp1_d_TUP2_bbw[(v20_1, v20_2)].remove(())
    else:
        _m_Comp1_d_TUP2_bbw[(v20_1, v20_2)].decref(())
    if (len(_m_Comp1_d_TUP2_bbw[(v20_1, v20_2)]) == 0):
        del _m_Comp1_d_TUP2_bbw[(v20_1, v20_2)]

def _maint_Comp1_d_TUP2_Comp1_T_tup1_add(_e):
    # Iterate {(v15__tup1, v15_a, v15__v1) : v15__tup1 in deltamatch(Comp1_T_tup1, 'b', _e, 1), (v15__tup1, v15_a, v15__v1) in _TUP2}
    v15__tup1 = _e
    if (isinstance(v15__tup1, tuple) and (len(v15__tup1) == 2)):
        for (v15_a, v15__v1) in setmatch({(v15__tup1, v15__tup1[0], v15__tup1[1])}, 'buu', v15__tup1):
            # Begin maint _m_Comp1_d_TUP2_bbw after "Comp1_d_TUP2.add((v15__tup1, v15_a, v15__v1))"
            _maint__m_Comp1_d_TUP2_bbw_add((v15__tup1, v15_a, v15__v1))
            # End maint _m_Comp1_d_TUP2_bbw after "Comp1_d_TUP2.add((v15__tup1, v15_a, v15__v1))"

def _maint_Comp1_d_TUP2_Comp1_T_tup1_remove(_e):
    # Iterate {(v16__tup1, v16_a, v16__v1) : v16__tup1 in deltamatch(Comp1_T_tup1, 'b', _e, 1), (v16__tup1, v16_a, v16__v1) in _TUP2}
    v16__tup1 = _e
    if (isinstance(v16__tup1, tuple) and (len(v16__tup1) == 2)):
        for (v16_a, v16__v1) in setmatch({(v16__tup1, v16__tup1[0], v16__tup1[1])}, 'buu', v16__tup1):
            # Begin maint _m_Comp1_d_TUP2_bbw before "Comp1_d_TUP2.remove((v16__tup1, v16_a, v16__v1))"
            _maint__m_Comp1_d_TUP2_bbw_remove((v16__tup1, v16_a, v16__v1))
            # End maint _m_Comp1_d_TUP2_bbw before "Comp1_d_TUP2.remove((v16__tup1, v16_a, v16__v1))"

Comp1_T_tup1 = RCSet()
def _maint_Comp1_T_tup1_Comp1_d_M_add(_e):
    # Iterate {(v13_s, v13__tup1) : (v13_s, v13__tup1) in deltamatch(Comp1_d_M, 'bb', _e, 1)}
    (v13_s, v13__tup1) = _e
    if (v13__tup1 not in Comp1_T_tup1):
        Comp1_T_tup1.add(v13__tup1)
        # Begin maint Comp1_d_TUP2 after "Comp1_T_tup1.add(v13__tup1)"
        _maint_Comp1_d_TUP2_Comp1_T_tup1_add(v13__tup1)
        # End maint Comp1_d_TUP2 after "Comp1_T_tup1.add(v13__tup1)"
    else:
        Comp1_T_tup1.incref(v13__tup1)

def _maint_Comp1_T_tup1_Comp1_d_M_remove(_e):
    # Iterate {(v14_s, v14__tup1) : (v14_s, v14__tup1) in deltamatch(Comp1_d_M, 'bb', _e, 1)}
    (v14_s, v14__tup1) = _e
    if (Comp1_T_tup1.getref(v14__tup1) == 1):
        # Begin maint Comp1_d_TUP2 before "Comp1_T_tup1.remove(v14__tup1)"
        _maint_Comp1_d_TUP2_Comp1_T_tup1_remove(v14__tup1)
        # End maint Comp1_d_TUP2 before "Comp1_T_tup1.remove(v14__tup1)"
        Comp1_T_tup1.remove(v14__tup1)
    else:
        Comp1_T_tup1.decref(v14__tup1)

Comp1_d_M = RCSet()
def _maint_Comp1_d_M_Comp1_Ts_add(_e):
    # Iterate {(v9_s, v9__tup1) : v9_s in deltamatch(Comp1_Ts, 'b', _e, 1), (v9_s, v9__tup1) in _M}
    v9_s = _e
    if isinstance(v9_s, Set):
        for v9__tup1 in v9_s:
            Comp1_d_M.add((v9_s, v9__tup1))
            # Begin maint _m_Comp1_d_M_in after "Comp1_d_M.add((v9_s, v9__tup1))"
            _maint__m_Comp1_d_M_in_add((v9_s, v9__tup1))
            # End maint _m_Comp1_d_M_in after "Comp1_d_M.add((v9_s, v9__tup1))"
            # Begin maint Comp1_T_tup1 after "Comp1_d_M.add((v9_s, v9__tup1))"
            _maint_Comp1_T_tup1_Comp1_d_M_add((v9_s, v9__tup1))
            # End maint Comp1_T_tup1 after "Comp1_d_M.add((v9_s, v9__tup1))"

def _maint_Comp1_d_M_Comp1_Ts_remove(_e):
    # Iterate {(v10_s, v10__tup1) : v10_s in deltamatch(Comp1_Ts, 'b', _e, 1), (v10_s, v10__tup1) in _M}
    v10_s = _e
    if isinstance(v10_s, Set):
        for v10__tup1 in v10_s:
            # Begin maint Comp1_T_tup1 before "Comp1_d_M.remove((v10_s, v10__tup1))"
            _maint_Comp1_T_tup1_Comp1_d_M_remove((v10_s, v10__tup1))
            # End maint Comp1_T_tup1 before "Comp1_d_M.remove((v10_s, v10__tup1))"
            # Begin maint _m_Comp1_d_M_in before "Comp1_d_M.remove((v10_s, v10__tup1))"
            _maint__m_Comp1_d_M_in_remove((v10_s, v10__tup1))
            # End maint _m_Comp1_d_M_in before "Comp1_d_M.remove((v10_s, v10__tup1))"
            Comp1_d_M.remove((v10_s, v10__tup1))

def _maint_Comp1_d_M__M_add(_e):
    # Iterate {(v11_s, v11__tup1) : v11_s in Comp1_Ts, (v11_s, v11__tup1) in deltamatch(_M, 'bb', _e, 1)}
    (v11_s, v11__tup1) = _e
    if (v11_s in Comp1_Ts):
        Comp1_d_M.add((v11_s, v11__tup1))
        # Begin maint _m_Comp1_d_M_in after "Comp1_d_M.add((v11_s, v11__tup1))"
        _maint__m_Comp1_d_M_in_add((v11_s, v11__tup1))
        # End maint _m_Comp1_d_M_in after "Comp1_d_M.add((v11_s, v11__tup1))"
        # Begin maint Comp1_T_tup1 after "Comp1_d_M.add((v11_s, v11__tup1))"
        _maint_Comp1_T_tup1_Comp1_d_M_add((v11_s, v11__tup1))
        # End maint Comp1_T_tup1 after "Comp1_d_M.add((v11_s, v11__tup1))"

Comp1_Ts = RCSet()
def _maint_Comp1_Ts__U_Comp1_add(_e):
    # Iterate {v7_s : v7_s in deltamatch(_U_Comp1, 'b', _e, 1)}
    v7_s = _e
    Comp1_Ts.add(v7_s)
    # Begin maint Comp1_d_M after "Comp1_Ts.add(v7_s)"
    _maint_Comp1_d_M_Comp1_Ts_add(v7_s)
    # End maint Comp1_d_M after "Comp1_Ts.add(v7_s)"

def _maint_Comp1_Ts__U_Comp1_remove(_e):
    # Iterate {v8_s : v8_s in deltamatch(_U_Comp1, 'b', _e, 1)}
    v8_s = _e
    # Begin maint Comp1_d_M before "Comp1_Ts.remove(v8_s)"
    _maint_Comp1_d_M_Comp1_Ts_remove(v8_s)
    # End maint Comp1_d_M before "Comp1_Ts.remove(v8_s)"
    Comp1_Ts.remove(v8_s)

Comp1 = RCSet()
def _maint_Comp1__U_Comp1_add(_e):
    # Iterate {(v1_s, v1__tup1, v1_a) : v1_s in deltamatch(_U_Comp1, 'b', _e, 1), (v1_s, v1__tup1) in _M, (v1__tup1, v1_a, _) in _TUP2, (v1_a > 1)}
    v1_s = _e
    if isinstance(v1_s, Set):
        for v1__tup1 in v1_s:
            if (isinstance(v1__tup1, tuple) and (len(v1__tup1) == 2)):
                for v1_a in setmatch({(v1__tup1, v1__tup1[0], v1__tup1[1])}, 'buw', v1__tup1):
                    if (v1_a > 1):
                        if ((v1_s, v1_a) not in Comp1):
                            Comp1.add((v1_s, v1_a))
                            # Begin maint _m_Comp1_out after "Comp1.add((v1_s, v1_a))"
                            _maint__m_Comp1_out_add((v1_s, v1_a))
                            # End maint _m_Comp1_out after "Comp1.add((v1_s, v1_a))"
                        else:
                            Comp1.incref((v1_s, v1_a))

def _maint_Comp1__U_Comp1_remove(_e):
    # Iterate {(v2_s, v2__tup1, v2_a) : v2_s in deltamatch(_U_Comp1, 'b', _e, 1), (v2_s, v2__tup1) in _M, (v2__tup1, v2_a, _) in _TUP2, (v2_a > 1)}
    v2_s = _e
    if isinstance(v2_s, Set):
        for v2__tup1 in v2_s:
            if (isinstance(v2__tup1, tuple) and (len(v2__tup1) == 2)):
                for v2_a in setmatch({(v2__tup1, v2__tup1[0], v2__tup1[1])}, 'buw', v2__tup1):
                    if (v2_a > 1):
                        if (Comp1.getref((v2_s, v2_a)) == 1):
                            # Begin maint _m_Comp1_out before "Comp1.remove((v2_s, v2_a))"
                            _maint__m_Comp1_out_remove((v2_s, v2_a))
                            # End maint _m_Comp1_out before "Comp1.remove((v2_s, v2_a))"
                            Comp1.remove((v2_s, v2_a))
                        else:
                            Comp1.decref((v2_s, v2_a))

def _maint_Comp1__M_add(_e):
    # Iterate {(v3_s, v3__tup1, v3_a) : v3_s in _U_Comp1, (v3_s, v3__tup1) in deltamatch(Comp1_d_M, 'bb', _e, 1), (v3_s, v3__tup1) in Comp1_d_M, (v3__tup1, v3_a, _) in _TUP2, (v3_a > 1)}
    (v3_s, v3__tup1) = _e
    if (v3_s in _U_Comp1):
        if ((v3_s, v3__tup1) in Comp1_d_M):
            if (isinstance(v3__tup1, tuple) and (len(v3__tup1) == 2)):
                for v3_a in setmatch({(v3__tup1, v3__tup1[0], v3__tup1[1])}, 'buw', v3__tup1):
                    if (v3_a > 1):
                        if ((v3_s, v3_a) not in Comp1):
                            Comp1.add((v3_s, v3_a))
                            # Begin maint _m_Comp1_out after "Comp1.add((v3_s, v3_a))"
                            _maint__m_Comp1_out_add((v3_s, v3_a))
                            # End maint _m_Comp1_out after "Comp1.add((v3_s, v3_a))"
                        else:
                            Comp1.incref((v3_s, v3_a))

_U_Comp1 = RCSet()
_UEXT_Comp1 = Set()
def demand_Comp1(s):
    '{(s, a) : s in _U_Comp1, (s, _tup1) in _M, (_tup1, a, _) in _TUP2, (a > 1)}'
    if (s not in _U_Comp1):
        _U_Comp1.add(s)
        # Begin maint Comp1_Ts after "_U_Comp1.add(s)"
        _maint_Comp1_Ts__U_Comp1_add(s)
        # End maint Comp1_Ts after "_U_Comp1.add(s)"
        # Begin maint Comp1 after "_U_Comp1.add(s)"
        _maint_Comp1__U_Comp1_add(s)
        # End maint Comp1 after "_U_Comp1.add(s)"
    else:
        _U_Comp1.incref(s)

def undemand_Comp1(s):
    '{(s, a) : s in _U_Comp1, (s, _tup1) in _M, (_tup1, a, _) in _TUP2, (a > 1)}'
    if (_U_Comp1.getref(s) == 1):
        # Begin maint Comp1 before "_U_Comp1.remove(s)"
        _maint_Comp1__U_Comp1_remove(s)
        # End maint Comp1 before "_U_Comp1.remove(s)"
        # Begin maint Comp1_Ts before "_U_Comp1.remove(s)"
        _maint_Comp1_Ts__U_Comp1_remove(s)
        # End maint Comp1_Ts before "_U_Comp1.remove(s)"
        _U_Comp1.remove(s)
    else:
        _U_Comp1.decref(s)

def query_Comp1(s):
    '{(s, a) : s in _U_Comp1, (s, _tup1) in _M, (_tup1, a, _) in _TUP2, (a > 1)}'
    if (s not in _UEXT_Comp1):
        _UEXT_Comp1.add(s)
        demand_Comp1(s)
    return True

s = Set()
for (x, y) in [(1, 2), (2, 3), (3, 4)]:
    s.add((x, y))
    # Begin maint Comp1_d_M after "_M.add((s, (x, y)))"
    _maint_Comp1_d_M__M_add((s, (x, y)))
    # End maint Comp1_d_M after "_M.add((s, (x, y)))"
    # Begin maint Comp1 after "_M.add((s, (x, y)))"
    _maint_Comp1__M_add((s, (x, y)))
    # End maint Comp1 after "_M.add((s, (x, y)))"
print(sorted((query_Comp1(s) and (_m_Comp1_out[s] if (s in _m_Comp1_out) else set()))))