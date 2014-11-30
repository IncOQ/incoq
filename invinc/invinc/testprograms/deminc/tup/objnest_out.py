from runtimelib import *
# Comp1 := {(s, x) : s in _U_Comp1, (s, _tup1) in _M, (_tup1, _tup2, z) in _TUP2, (_tup2, x, y) in _TUP2, ((x + y) == z)}
# Comp1_Ts := {s : s in _U_Comp1}
# Comp1_d_M := {(s, _tup1) : s in Comp1_Ts, (s, _tup1) in _M}
# Comp1_T_tup1 := {_tup1 : (s, _tup1) in Comp1_d_M}
# Comp1_d_TUP21 := {(_tup1, _tup2, z) : _tup1 in Comp1_T_tup1, (_tup1, _tup2, z) in _TUP2}
# Comp1_T_tup2 := {_tup2 : (_tup1, _tup2, z) in Comp1_d_TUP21}
# Comp1_d_TUP22 := {(_tup2, x, y) : _tup2 in Comp1_T_tup2, (_tup2, x, y) in _TUP2}
_m_Comp1_out = Map()
def _maint__m_Comp1_out_add(_e):
    (v29_1, v29_2) = _e
    if (v29_1 not in _m_Comp1_out):
        _m_Comp1_out[v29_1] = set()
    _m_Comp1_out[v29_1].add(v29_2)

def _maint__m_Comp1_out_remove(_e):
    (v30_1, v30_2) = _e
    _m_Comp1_out[v30_1].remove(v30_2)
    if (len(_m_Comp1_out[v30_1]) == 0):
        del _m_Comp1_out[v30_1]

_m_Comp1_d_TUP21_ubu = Map()
def _maint__m_Comp1_d_TUP21_ubu_add(_e):
    (v27_1, v27_2, v27_3) = _e
    if (v27_2 not in _m_Comp1_d_TUP21_ubu):
        _m_Comp1_d_TUP21_ubu[v27_2] = set()
    _m_Comp1_d_TUP21_ubu[v27_2].add((v27_1, v27_3))

def _maint__m_Comp1_d_TUP21_ubu_remove(_e):
    (v28_1, v28_2, v28_3) = _e
    _m_Comp1_d_TUP21_ubu[v28_2].remove((v28_1, v28_3))
    if (len(_m_Comp1_d_TUP21_ubu[v28_2]) == 0):
        del _m_Comp1_d_TUP21_ubu[v28_2]

_m_Comp1_d_M_in = Map()
def _maint__m_Comp1_d_M_in_add(_e):
    (v25_1, v25_2) = _e
    if (v25_2 not in _m_Comp1_d_M_in):
        _m_Comp1_d_M_in[v25_2] = set()
    _m_Comp1_d_M_in[v25_2].add(v25_1)

def _maint__m_Comp1_d_M_in_remove(_e):
    (v26_1, v26_2) = _e
    _m_Comp1_d_M_in[v26_2].remove(v26_1)
    if (len(_m_Comp1_d_M_in[v26_2]) == 0):
        del _m_Comp1_d_M_in[v26_2]

Comp1_d_TUP22 = RCSet()
def _maint_Comp1_d_TUP22_Comp1_T_tup2_add(_e):
    # Iterate {(v21__tup2, v21_x, v21_y) : v21__tup2 in deltamatch(Comp1_T_tup2, 'b', _e, 1), (v21__tup2, v21_x, v21_y) in _TUP2}
    v21__tup2 = _e
    if (isinstance(v21__tup2, tuple) and (len(v21__tup2) == 2)):
        for (v21_x, v21_y) in setmatch({(v21__tup2, v21__tup2[0], v21__tup2[1])}, 'buu', v21__tup2):
            Comp1_d_TUP22.add((v21__tup2, v21_x, v21_y))

def _maint_Comp1_d_TUP22_Comp1_T_tup2_remove(_e):
    # Iterate {(v22__tup2, v22_x, v22_y) : v22__tup2 in deltamatch(Comp1_T_tup2, 'b', _e, 1), (v22__tup2, v22_x, v22_y) in _TUP2}
    v22__tup2 = _e
    if (isinstance(v22__tup2, tuple) and (len(v22__tup2) == 2)):
        for (v22_x, v22_y) in setmatch({(v22__tup2, v22__tup2[0], v22__tup2[1])}, 'buu', v22__tup2):
            Comp1_d_TUP22.remove((v22__tup2, v22_x, v22_y))

Comp1_T_tup2 = RCSet()
def _maint_Comp1_T_tup2_Comp1_d_TUP21_add(_e):
    # Iterate {(v19__tup1, v19__tup2, v19_z) : (v19__tup1, v19__tup2, v19_z) in deltamatch(Comp1_d_TUP21, 'bbb', _e, 1)}
    (v19__tup1, v19__tup2, v19_z) = _e
    if (v19__tup2 not in Comp1_T_tup2):
        Comp1_T_tup2.add(v19__tup2)
        # Begin maint Comp1_d_TUP22 after "Comp1_T_tup2.add(v19__tup2)"
        _maint_Comp1_d_TUP22_Comp1_T_tup2_add(v19__tup2)
        # End maint Comp1_d_TUP22 after "Comp1_T_tup2.add(v19__tup2)"
    else:
        Comp1_T_tup2.incref(v19__tup2)

def _maint_Comp1_T_tup2_Comp1_d_TUP21_remove(_e):
    # Iterate {(v20__tup1, v20__tup2, v20_z) : (v20__tup1, v20__tup2, v20_z) in deltamatch(Comp1_d_TUP21, 'bbb', _e, 1)}
    (v20__tup1, v20__tup2, v20_z) = _e
    if (Comp1_T_tup2.getref(v20__tup2) == 1):
        # Begin maint Comp1_d_TUP22 before "Comp1_T_tup2.remove(v20__tup2)"
        _maint_Comp1_d_TUP22_Comp1_T_tup2_remove(v20__tup2)
        # End maint Comp1_d_TUP22 before "Comp1_T_tup2.remove(v20__tup2)"
        Comp1_T_tup2.remove(v20__tup2)
    else:
        Comp1_T_tup2.decref(v20__tup2)

Comp1_d_TUP21 = RCSet()
def _maint_Comp1_d_TUP21_Comp1_T_tup1_add(_e):
    # Iterate {(v15__tup1, v15__tup2, v15_z) : v15__tup1 in deltamatch(Comp1_T_tup1, 'b', _e, 1), (v15__tup1, v15__tup2, v15_z) in _TUP2}
    v15__tup1 = _e
    if (isinstance(v15__tup1, tuple) and (len(v15__tup1) == 2)):
        for (v15__tup2, v15_z) in setmatch({(v15__tup1, v15__tup1[0], v15__tup1[1])}, 'buu', v15__tup1):
            Comp1_d_TUP21.add((v15__tup1, v15__tup2, v15_z))
            # Begin maint _m_Comp1_d_TUP21_ubu after "Comp1_d_TUP21.add((v15__tup1, v15__tup2, v15_z))"
            _maint__m_Comp1_d_TUP21_ubu_add((v15__tup1, v15__tup2, v15_z))
            # End maint _m_Comp1_d_TUP21_ubu after "Comp1_d_TUP21.add((v15__tup1, v15__tup2, v15_z))"
            # Begin maint Comp1_T_tup2 after "Comp1_d_TUP21.add((v15__tup1, v15__tup2, v15_z))"
            _maint_Comp1_T_tup2_Comp1_d_TUP21_add((v15__tup1, v15__tup2, v15_z))
            # End maint Comp1_T_tup2 after "Comp1_d_TUP21.add((v15__tup1, v15__tup2, v15_z))"

def _maint_Comp1_d_TUP21_Comp1_T_tup1_remove(_e):
    # Iterate {(v16__tup1, v16__tup2, v16_z) : v16__tup1 in deltamatch(Comp1_T_tup1, 'b', _e, 1), (v16__tup1, v16__tup2, v16_z) in _TUP2}
    v16__tup1 = _e
    if (isinstance(v16__tup1, tuple) and (len(v16__tup1) == 2)):
        for (v16__tup2, v16_z) in setmatch({(v16__tup1, v16__tup1[0], v16__tup1[1])}, 'buu', v16__tup1):
            # Begin maint Comp1_T_tup2 before "Comp1_d_TUP21.remove((v16__tup1, v16__tup2, v16_z))"
            _maint_Comp1_T_tup2_Comp1_d_TUP21_remove((v16__tup1, v16__tup2, v16_z))
            # End maint Comp1_T_tup2 before "Comp1_d_TUP21.remove((v16__tup1, v16__tup2, v16_z))"
            # Begin maint _m_Comp1_d_TUP21_ubu before "Comp1_d_TUP21.remove((v16__tup1, v16__tup2, v16_z))"
            _maint__m_Comp1_d_TUP21_ubu_remove((v16__tup1, v16__tup2, v16_z))
            # End maint _m_Comp1_d_TUP21_ubu before "Comp1_d_TUP21.remove((v16__tup1, v16__tup2, v16_z))"
            Comp1_d_TUP21.remove((v16__tup1, v16__tup2, v16_z))

Comp1_T_tup1 = RCSet()
def _maint_Comp1_T_tup1_Comp1_d_M_add(_e):
    # Iterate {(v13_s, v13__tup1) : (v13_s, v13__tup1) in deltamatch(Comp1_d_M, 'bb', _e, 1)}
    (v13_s, v13__tup1) = _e
    if (v13__tup1 not in Comp1_T_tup1):
        Comp1_T_tup1.add(v13__tup1)
        # Begin maint Comp1_d_TUP21 after "Comp1_T_tup1.add(v13__tup1)"
        _maint_Comp1_d_TUP21_Comp1_T_tup1_add(v13__tup1)
        # End maint Comp1_d_TUP21 after "Comp1_T_tup1.add(v13__tup1)"
    else:
        Comp1_T_tup1.incref(v13__tup1)

def _maint_Comp1_T_tup1_Comp1_d_M_remove(_e):
    # Iterate {(v14_s, v14__tup1) : (v14_s, v14__tup1) in deltamatch(Comp1_d_M, 'bb', _e, 1)}
    (v14_s, v14__tup1) = _e
    if (Comp1_T_tup1.getref(v14__tup1) == 1):
        # Begin maint Comp1_d_TUP21 before "Comp1_T_tup1.remove(v14__tup1)"
        _maint_Comp1_d_TUP21_Comp1_T_tup1_remove(v14__tup1)
        # End maint Comp1_d_TUP21 before "Comp1_T_tup1.remove(v14__tup1)"
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
    # Iterate {(v1_s, v1__tup1, v1__tup2, v1_z, v1_x, v1_y) : v1_s in deltamatch(_U_Comp1, 'b', _e, 1), (v1_s, v1__tup1) in _M, (v1__tup1, v1__tup2, v1_z) in _TUP2, (v1__tup2, v1_x, v1_y) in _TUP2, ((v1_x + v1_y) == v1_z)}
    v1_s = _e
    if isinstance(v1_s, Set):
        for v1__tup1 in v1_s:
            if (isinstance(v1__tup1, tuple) and (len(v1__tup1) == 2)):
                for (v1__tup2, v1_z) in setmatch({(v1__tup1, v1__tup1[0], v1__tup1[1])}, 'buu', v1__tup1):
                    if (isinstance(v1__tup2, tuple) and (len(v1__tup2) == 2)):
                        for (v1_x, v1_y) in setmatch({(v1__tup2, v1__tup2[0], v1__tup2[1])}, 'buu', v1__tup2):
                            if ((v1_x + v1_y) == v1_z):
                                if ((v1_s, v1_x) not in Comp1):
                                    Comp1.add((v1_s, v1_x))
                                    # Begin maint _m_Comp1_out after "Comp1.add((v1_s, v1_x))"
                                    _maint__m_Comp1_out_add((v1_s, v1_x))
                                    # End maint _m_Comp1_out after "Comp1.add((v1_s, v1_x))"
                                else:
                                    Comp1.incref((v1_s, v1_x))

def _maint_Comp1__U_Comp1_remove(_e):
    # Iterate {(v2_s, v2__tup1, v2__tup2, v2_z, v2_x, v2_y) : v2_s in deltamatch(_U_Comp1, 'b', _e, 1), (v2_s, v2__tup1) in _M, (v2__tup1, v2__tup2, v2_z) in _TUP2, (v2__tup2, v2_x, v2_y) in _TUP2, ((v2_x + v2_y) == v2_z)}
    v2_s = _e
    if isinstance(v2_s, Set):
        for v2__tup1 in v2_s:
            if (isinstance(v2__tup1, tuple) and (len(v2__tup1) == 2)):
                for (v2__tup2, v2_z) in setmatch({(v2__tup1, v2__tup1[0], v2__tup1[1])}, 'buu', v2__tup1):
                    if (isinstance(v2__tup2, tuple) and (len(v2__tup2) == 2)):
                        for (v2_x, v2_y) in setmatch({(v2__tup2, v2__tup2[0], v2__tup2[1])}, 'buu', v2__tup2):
                            if ((v2_x + v2_y) == v2_z):
                                if (Comp1.getref((v2_s, v2_x)) == 1):
                                    # Begin maint _m_Comp1_out before "Comp1.remove((v2_s, v2_x))"
                                    _maint__m_Comp1_out_remove((v2_s, v2_x))
                                    # End maint _m_Comp1_out before "Comp1.remove((v2_s, v2_x))"
                                    Comp1.remove((v2_s, v2_x))
                                else:
                                    Comp1.decref((v2_s, v2_x))

def _maint_Comp1__M_add(_e):
    # Iterate {(v3_s, v3__tup1, v3__tup2, v3_z, v3_x, v3_y) : v3_s in _U_Comp1, (v3_s, v3__tup1) in deltamatch(Comp1_d_M, 'bb', _e, 1), (v3_s, v3__tup1) in Comp1_d_M, (v3__tup1, v3__tup2, v3_z) in _TUP2, (v3__tup2, v3_x, v3_y) in _TUP2, ((v3_x + v3_y) == v3_z)}
    (v3_s, v3__tup1) = _e
    if (v3_s in _U_Comp1):
        if ((v3_s, v3__tup1) in Comp1_d_M):
            if (isinstance(v3__tup1, tuple) and (len(v3__tup1) == 2)):
                for (v3__tup2, v3_z) in setmatch({(v3__tup1, v3__tup1[0], v3__tup1[1])}, 'buu', v3__tup1):
                    if (isinstance(v3__tup2, tuple) and (len(v3__tup2) == 2)):
                        for (v3_x, v3_y) in setmatch({(v3__tup2, v3__tup2[0], v3__tup2[1])}, 'buu', v3__tup2):
                            if ((v3_x + v3_y) == v3_z):
                                if ((v3_s, v3_x) not in Comp1):
                                    Comp1.add((v3_s, v3_x))
                                    # Begin maint _m_Comp1_out after "Comp1.add((v3_s, v3_x))"
                                    _maint__m_Comp1_out_add((v3_s, v3_x))
                                    # End maint _m_Comp1_out after "Comp1.add((v3_s, v3_x))"
                                else:
                                    Comp1.incref((v3_s, v3_x))

_U_Comp1 = RCSet()
_UEXT_Comp1 = Set()
def demand_Comp1(s):
    '{(s, x) : s in _U_Comp1, (s, _tup1) in _M, (_tup1, _tup2, z) in _TUP2, (_tup2, x, y) in _TUP2, ((x + y) == z)}'
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
    '{(s, x) : s in _U_Comp1, (s, _tup1) in _M, (_tup1, _tup2, z) in _TUP2, (_tup2, x, y) in _TUP2, ((x + y) == z)}'
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
    '{(s, x) : s in _U_Comp1, (s, _tup1) in _M, (_tup1, _tup2, z) in _TUP2, (_tup2, x, y) in _TUP2, ((x + y) == z)}'
    if (s not in _UEXT_Comp1):
        _UEXT_Comp1.add(s)
        demand_Comp1(s)
    return True

s1 = Set()
for i in [1, 2, 3]:
    s1.add(((i, (2 * i)), (3 * i)))
    # Begin maint Comp1_d_M after "_M.add((s1, ((i, (2 * i)), (3 * i))))"
    _maint_Comp1_d_M__M_add((s1, ((i, (2 * i)), (3 * i))))
    # End maint Comp1_d_M after "_M.add((s1, ((i, (2 * i)), (3 * i))))"
    # Begin maint Comp1 after "_M.add((s1, ((i, (2 * i)), (3 * i))))"
    _maint_Comp1__M_add((s1, ((i, (2 * i)), (3 * i))))
    # End maint Comp1 after "_M.add((s1, ((i, (2 * i)), (3 * i))))"
    s1.add((((2 * i), (3 * i)), (4 * i)))
    # Begin maint Comp1_d_M after "_M.add((s1, (((2 * i), (3 * i)), (4 * i))))"
    _maint_Comp1_d_M__M_add((s1, (((2 * i), (3 * i)), (4 * i))))
    # End maint Comp1_d_M after "_M.add((s1, (((2 * i), (3 * i)), (4 * i))))"
    # Begin maint Comp1 after "_M.add((s1, (((2 * i), (3 * i)), (4 * i))))"
    _maint_Comp1__M_add((s1, (((2 * i), (3 * i)), (4 * i))))
    # End maint Comp1 after "_M.add((s1, (((2 * i), (3 * i)), (4 * i))))"
s = s1
print(sorted((query_Comp1(s) and (_m_Comp1_out[s] if (s in _m_Comp1_out) else set()))))