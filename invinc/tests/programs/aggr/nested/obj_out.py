from invinc.runtime import *
# Comp1 := {(o, _e) : o in _U_Comp1, (o, o_f) in _F_f, (o_f, _e) in _M}
# Aggr1 := sum(DEMQUERY(Comp1, [o], setmatch(Comp1, 'bu', o)), None)
# Comp8 := {(s, _av1) : s in _U_Comp8, (s, o) in _M, _av1 in {Aggr1.smlookup('bu', o, None)}}
# Comp8_Ts := {s : s in _U_Comp8}
# Comp8_d_M := {(s, o) : s in Comp8_Ts, (s, o) in _M}
# Comp8_To := {o : (s, o) in Comp8_d_M}
# Aggr1_delta := {o : o in Comp8_To}
_m_Comp8_out = Map()
def _maint__m_Comp8_out_add(_e):
    (v40_1, v40_2) = _e
    if (v40_1 not in _m_Comp8_out):
        _m_Comp8_out[v40_1] = set()
    _m_Comp8_out[v40_1].add(v40_2)

def _maint__m_Comp8_out_remove(_e):
    (v41_1, v41_2) = _e
    _m_Comp8_out[v41_1].remove(v41_2)
    if (len(_m_Comp8_out[v41_1]) == 0):
        del _m_Comp8_out[v41_1]

_m__F_f_in = Map()
def _maint__m__F_f_in_add(_e):
    (v38_1, v38_2) = _e
    if (v38_2 not in _m__F_f_in):
        _m__F_f_in[v38_2] = set()
    _m__F_f_in[v38_2].add(v38_1)

_m_Comp1_out = Map()
def _maint__m_Comp1_out_add(_e):
    (v36_1, v36_2) = _e
    if (v36_1 not in _m_Comp1_out):
        _m_Comp1_out[v36_1] = set()
    _m_Comp1_out[v36_1].add(v36_2)

def _maint__m_Comp1_out_remove(_e):
    (v37_1, v37_2) = _e
    _m_Comp1_out[v37_1].remove(v37_2)
    if (len(_m_Comp1_out[v37_1]) == 0):
        del _m_Comp1_out[v37_1]

_m_Comp8_d_M_in = Map()
def _maint__m_Comp8_d_M_in_add(_e):
    (v34_1, v34_2) = _e
    if (v34_2 not in _m_Comp8_d_M_in):
        _m_Comp8_d_M_in[v34_2] = set()
    _m_Comp8_d_M_in[v34_2].add(v34_1)

def _maint__m_Comp8_d_M_in_remove(_e):
    (v35_1, v35_2) = _e
    _m_Comp8_d_M_in[v35_2].remove(v35_1)
    if (len(_m_Comp8_d_M_in[v35_2]) == 0):
        del _m_Comp8_d_M_in[v35_2]

_m_Aggr1_out = Map()
def _maint__m_Aggr1_out_add(_e):
    (v32_1, v32_2) = _e
    if (v32_1 not in _m_Aggr1_out):
        _m_Aggr1_out[v32_1] = set()
    _m_Aggr1_out[v32_1].add(v32_2)

def _maint__m_Aggr1_out_remove(_e):
    (v33_1, v33_2) = _e
    _m_Aggr1_out[v33_1].remove(v33_2)
    if (len(_m_Aggr1_out[v33_1]) == 0):
        del _m_Aggr1_out[v33_1]

Aggr1_delta = RCSet()
def _maint_Aggr1_delta_Comp8_To_add(_e):
    # Iterate {v26_o : v26_o in deltamatch(Comp8_To, 'b', _e, 1)}
    v26_o = _e
    Aggr1_delta.add(v26_o)

Comp8_To = RCSet()
def _maint_Comp8_To_Comp8_d_M_add(_e):
    # Iterate {(v24_s, v24_o) : (v24_s, v24_o) in deltamatch(Comp8_d_M, 'bb', _e, 1)}
    (v24_s, v24_o) = _e
    if (v24_o not in Comp8_To):
        Comp8_To.add(v24_o)
        # Begin maint Aggr1_delta after "Comp8_To.add(v24_o)"
        _maint_Aggr1_delta_Comp8_To_add(v24_o)
        # End maint Aggr1_delta after "Comp8_To.add(v24_o)"
    else:
        Comp8_To.incref(v24_o)

def _maint_Comp8_To_Comp8_d_M_remove(_e):
    # Iterate {(v25_s, v25_o) : (v25_s, v25_o) in deltamatch(Comp8_d_M, 'bb', _e, 1)}
    (v25_s, v25_o) = _e
    if (Comp8_To.getref(v25_o) == 1):
        # Begin maint Aggr1_delta before "Comp8_To.remove(v25_o)"
        _maint_Aggr1_delta_Comp8_To_add(v25_o)
        # End maint Aggr1_delta before "Comp8_To.remove(v25_o)"
        Comp8_To.remove(v25_o)
    else:
        Comp8_To.decref(v25_o)

Comp8_d_M = RCSet()
def _maint_Comp8_d_M_Comp8_Ts_add(_e):
    # Iterate {(v20_s, v20_o) : v20_s in deltamatch(Comp8_Ts, 'b', _e, 1), (v20_s, v20_o) in _M}
    v20_s = _e
    if isinstance(v20_s, Set):
        for v20_o in v20_s:
            Comp8_d_M.add((v20_s, v20_o))
            # Begin maint _m_Comp8_d_M_in after "Comp8_d_M.add((v20_s, v20_o))"
            _maint__m_Comp8_d_M_in_add((v20_s, v20_o))
            # End maint _m_Comp8_d_M_in after "Comp8_d_M.add((v20_s, v20_o))"
            # Begin maint Comp8_To after "Comp8_d_M.add((v20_s, v20_o))"
            _maint_Comp8_To_Comp8_d_M_add((v20_s, v20_o))
            # End maint Comp8_To after "Comp8_d_M.add((v20_s, v20_o))"

def _maint_Comp8_d_M_Comp8_Ts_remove(_e):
    # Iterate {(v21_s, v21_o) : v21_s in deltamatch(Comp8_Ts, 'b', _e, 1), (v21_s, v21_o) in _M}
    v21_s = _e
    if isinstance(v21_s, Set):
        for v21_o in v21_s:
            # Begin maint Comp8_To before "Comp8_d_M.remove((v21_s, v21_o))"
            _maint_Comp8_To_Comp8_d_M_remove((v21_s, v21_o))
            # End maint Comp8_To before "Comp8_d_M.remove((v21_s, v21_o))"
            # Begin maint _m_Comp8_d_M_in before "Comp8_d_M.remove((v21_s, v21_o))"
            _maint__m_Comp8_d_M_in_remove((v21_s, v21_o))
            # End maint _m_Comp8_d_M_in before "Comp8_d_M.remove((v21_s, v21_o))"
            Comp8_d_M.remove((v21_s, v21_o))

def _maint_Comp8_d_M__M_add(_e):
    # Iterate {(v22_s, v22_o) : v22_s in Comp8_Ts, (v22_s, v22_o) in deltamatch(_M, 'bb', _e, 1)}
    (v22_s, v22_o) = _e
    if (v22_s in Comp8_Ts):
        Comp8_d_M.add((v22_s, v22_o))
        # Begin maint _m_Comp8_d_M_in after "Comp8_d_M.add((v22_s, v22_o))"
        _maint__m_Comp8_d_M_in_add((v22_s, v22_o))
        # End maint _m_Comp8_d_M_in after "Comp8_d_M.add((v22_s, v22_o))"
        # Begin maint Comp8_To after "Comp8_d_M.add((v22_s, v22_o))"
        _maint_Comp8_To_Comp8_d_M_add((v22_s, v22_o))
        # End maint Comp8_To after "Comp8_d_M.add((v22_s, v22_o))"

Comp8_Ts = RCSet()
def _maint_Comp8_Ts__U_Comp8_add(_e):
    # Iterate {v18_s : v18_s in deltamatch(_U_Comp8, 'b', _e, 1)}
    v18_s = _e
    Comp8_Ts.add(v18_s)
    # Begin maint Comp8_d_M after "Comp8_Ts.add(v18_s)"
    _maint_Comp8_d_M_Comp8_Ts_add(v18_s)
    # End maint Comp8_d_M after "Comp8_Ts.add(v18_s)"

def _maint_Comp8_Ts__U_Comp8_remove(_e):
    # Iterate {v19_s : v19_s in deltamatch(_U_Comp8, 'b', _e, 1)}
    v19_s = _e
    # Begin maint Comp8_d_M before "Comp8_Ts.remove(v19_s)"
    _maint_Comp8_d_M_Comp8_Ts_remove(v19_s)
    # End maint Comp8_d_M before "Comp8_Ts.remove(v19_s)"
    Comp8_Ts.remove(v19_s)

Comp8 = RCSet()
def _maint_Comp8__U_Comp8_add(_e):
    # Iterate {(v12_s, v12_o, v12__av1) : v12_s in deltamatch(_U_Comp8, 'b', _e, 1), (v12_s, v12_o) in _M, v12__av1 in {Aggr1.smlookup('bu', v12_o, None)}}
    v12_s = _e
    if isinstance(v12_s, Set):
        for v12_o in v12_s:
            for v12__av1 in (_m_Aggr1_out[v12_o] if (v12_o in _m_Aggr1_out) else set()):
                if ((v12_s, v12__av1) not in Comp8):
                    Comp8.add((v12_s, v12__av1))
                    # Begin maint _m_Comp8_out after "Comp8.add((v12_s, v12__av1))"
                    _maint__m_Comp8_out_add((v12_s, v12__av1))
                    # End maint _m_Comp8_out after "Comp8.add((v12_s, v12__av1))"
                else:
                    Comp8.incref((v12_s, v12__av1))

def _maint_Comp8__U_Comp8_remove(_e):
    # Iterate {(v13_s, v13_o, v13__av1) : v13_s in deltamatch(_U_Comp8, 'b', _e, 1), (v13_s, v13_o) in _M, v13__av1 in {Aggr1.smlookup('bu', v13_o, None)}}
    v13_s = _e
    if isinstance(v13_s, Set):
        for v13_o in v13_s:
            for v13__av1 in (_m_Aggr1_out[v13_o] if (v13_o in _m_Aggr1_out) else set()):
                if (Comp8.getref((v13_s, v13__av1)) == 1):
                    # Begin maint _m_Comp8_out before "Comp8.remove((v13_s, v13__av1))"
                    _maint__m_Comp8_out_remove((v13_s, v13__av1))
                    # End maint _m_Comp8_out before "Comp8.remove((v13_s, v13__av1))"
                    Comp8.remove((v13_s, v13__av1))
                else:
                    Comp8.decref((v13_s, v13__av1))

def _maint_Comp8__M_add(_e):
    # Iterate {(v14_s, v14_o, v14__av1) : v14_s in _U_Comp8, (v14_s, v14_o) in deltamatch(Comp8_d_M, 'bb', _e, 1), (v14_s, v14_o) in Comp8_d_M, v14__av1 in {Aggr1.smlookup('bu', v14_o, None)}}
    (v14_s, v14_o) = _e
    if (v14_s in _U_Comp8):
        if ((v14_s, v14_o) in Comp8_d_M):
            for v14__av1 in (_m_Aggr1_out[v14_o] if (v14_o in _m_Aggr1_out) else set()):
                if ((v14_s, v14__av1) not in Comp8):
                    Comp8.add((v14_s, v14__av1))
                    # Begin maint _m_Comp8_out after "Comp8.add((v14_s, v14__av1))"
                    _maint__m_Comp8_out_add((v14_s, v14__av1))
                    # End maint _m_Comp8_out after "Comp8.add((v14_s, v14__av1))"
                else:
                    Comp8.incref((v14_s, v14__av1))

def _maint_Comp8_Aggr1_add(_e):
    # Iterate {(v16_s, v16_o, v16__av1) : v16_s in _U_Comp8, (v16_s, v16_o) in Comp8_d_M, (v16_o, v16__av1) in deltamatch(Aggr1, 'bb', _e, 1)}
    (v16_o, v16__av1) = _e
    for v16_s in (_m_Comp8_d_M_in[v16_o] if (v16_o in _m_Comp8_d_M_in) else set()):
        if (v16_s in _U_Comp8):
            if ((v16_s, v16__av1) not in Comp8):
                Comp8.add((v16_s, v16__av1))
                # Begin maint _m_Comp8_out after "Comp8.add((v16_s, v16__av1))"
                _maint__m_Comp8_out_add((v16_s, v16__av1))
                # End maint _m_Comp8_out after "Comp8.add((v16_s, v16__av1))"
            else:
                Comp8.incref((v16_s, v16__av1))

def _maint_Comp8_Aggr1_remove(_e):
    # Iterate {(v17_s, v17_o, v17__av1) : v17_s in _U_Comp8, (v17_s, v17_o) in Comp8_d_M, (v17_o, v17__av1) in deltamatch(Aggr1, 'bb', _e, 1)}
    (v17_o, v17__av1) = _e
    for v17_s in (_m_Comp8_d_M_in[v17_o] if (v17_o in _m_Comp8_d_M_in) else set()):
        if (v17_s in _U_Comp8):
            if (Comp8.getref((v17_s, v17__av1)) == 1):
                # Begin maint _m_Comp8_out before "Comp8.remove((v17_s, v17__av1))"
                _maint__m_Comp8_out_remove((v17_s, v17__av1))
                # End maint _m_Comp8_out before "Comp8.remove((v17_s, v17__av1))"
                Comp8.remove((v17_s, v17__av1))
            else:
                Comp8.decref((v17_s, v17__av1))

_U_Comp8 = RCSet()
_UEXT_Comp8 = Set()
def demand_Comp8(s):
    "{(s, _av1) : s in _U_Comp8, (s, o) in _M, _av1 in {Aggr1.smlookup('bu', o, None)}}"
    if (s not in _U_Comp8):
        _U_Comp8.add(s)
        # Begin maint Comp8_Ts after "_U_Comp8.add(s)"
        _maint_Comp8_Ts__U_Comp8_add(s)
        # End maint Comp8_Ts after "_U_Comp8.add(s)"
        # Begin maint Comp8 after "_U_Comp8.add(s)"
        _maint_Comp8__U_Comp8_add(s)
        # End maint Comp8 after "_U_Comp8.add(s)"
        # Begin maint demand_Aggr1 after "_U_Comp8.add(s)"
        for v28_o in Aggr1_delta.elements():
            demand_Aggr1(v28_o)
        Aggr1_delta.clear()
        # End maint demand_Aggr1 after "_U_Comp8.add(s)"
    else:
        _U_Comp8.incref(s)

def undemand_Comp8(s):
    "{(s, _av1) : s in _U_Comp8, (s, o) in _M, _av1 in {Aggr1.smlookup('bu', o, None)}}"
    if (_U_Comp8.getref(s) == 1):
        # Begin maint Comp8 before "_U_Comp8.remove(s)"
        _maint_Comp8__U_Comp8_remove(s)
        # End maint Comp8 before "_U_Comp8.remove(s)"
        # Begin maint Comp8_Ts before "_U_Comp8.remove(s)"
        _maint_Comp8_Ts__U_Comp8_remove(s)
        # End maint Comp8_Ts before "_U_Comp8.remove(s)"
        _U_Comp8.remove(s)
        # Begin maint undemand_Aggr1 after "_U_Comp8.remove(s)"
        for v29_o in Aggr1_delta.elements():
            undemand_Aggr1(v29_o)
        Aggr1_delta.clear()
        # End maint undemand_Aggr1 after "_U_Comp8.remove(s)"
    else:
        _U_Comp8.decref(s)

def query_Comp8(s):
    "{(s, _av1) : s in _U_Comp8, (s, o) in _M, _av1 in {Aggr1.smlookup('bu', o, None)}}"
    if (s not in _UEXT_Comp8):
        _UEXT_Comp8.add(s)
        demand_Comp8(s)
    return True

def _maint_Aggr1_add(_e):
    (v8_v1, v8_v2) = _e
    if (v8_v1 in _U_Aggr1):
        v8_val = _m_Aggr1_out.singlelookup(v8_v1)
        v8_val = (v8_val + v8_v2)
        v8_1 = v8_v1
        v8_elem = _m_Aggr1_out.singlelookup(v8_v1)
        # Begin maint Comp8 before "Aggr1.remove((v8_1, v8_elem))"
        _maint_Comp8_Aggr1_remove((v8_1, v8_elem))
        # End maint Comp8 before "Aggr1.remove((v8_1, v8_elem))"
        # Begin maint _m_Aggr1_out before "Aggr1.remove((v8_1, v8_elem))"
        _maint__m_Aggr1_out_remove((v8_1, v8_elem))
        # End maint _m_Aggr1_out before "Aggr1.remove((v8_1, v8_elem))"
        # Begin maint _m_Aggr1_out after "Aggr1.add((v8_1, v8_val))"
        _maint__m_Aggr1_out_add((v8_1, v8_val))
        # End maint _m_Aggr1_out after "Aggr1.add((v8_1, v8_val))"
        # Begin maint Comp8 after "Aggr1.add((v8_1, v8_val))"
        _maint_Comp8_Aggr1_add((v8_1, v8_val))
        # End maint Comp8 after "Aggr1.add((v8_1, v8_val))"

def _maint_Aggr1_remove(_e):
    (v9_v1, v9_v2) = _e
    if (v9_v1 in _U_Aggr1):
        v9_val = _m_Aggr1_out.singlelookup(v9_v1)
        v9_val = (v9_val - v9_v2)
        v9_1 = v9_v1
        v9_elem = _m_Aggr1_out.singlelookup(v9_v1)
        # Begin maint Comp8 before "Aggr1.remove((v9_1, v9_elem))"
        _maint_Comp8_Aggr1_remove((v9_1, v9_elem))
        # End maint Comp8 before "Aggr1.remove((v9_1, v9_elem))"
        # Begin maint _m_Aggr1_out before "Aggr1.remove((v9_1, v9_elem))"
        _maint__m_Aggr1_out_remove((v9_1, v9_elem))
        # End maint _m_Aggr1_out before "Aggr1.remove((v9_1, v9_elem))"
        # Begin maint _m_Aggr1_out after "Aggr1.add((v9_1, v9_val))"
        _maint__m_Aggr1_out_add((v9_1, v9_val))
        # End maint _m_Aggr1_out after "Aggr1.add((v9_1, v9_val))"
        # Begin maint Comp8 after "Aggr1.add((v9_1, v9_val))"
        _maint_Comp8_Aggr1_add((v9_1, v9_val))
        # End maint Comp8 after "Aggr1.add((v9_1, v9_val))"

_U_Aggr1 = RCSet()
_UEXT_Aggr1 = Set()
def demand_Aggr1(o):
    "sum(DEMQUERY(Comp1, [o], setmatch(Comp1, 'bu', o)), None)"
    if (o not in _U_Aggr1):
        _U_Aggr1.add(o)
        # Begin maint Aggr1 after "_U_Aggr1.add(o)"
        v10_val = 0
        for v10_elem in (_m_Comp1_out[o] if (o in _m_Comp1_out) else set()):
            v10_val = (v10_val + v10_elem)
        v10_1 = o
        # Begin maint _m_Aggr1_out after "Aggr1.add((v10_1, v10_val))"
        _maint__m_Aggr1_out_add((v10_1, v10_val))
        # End maint _m_Aggr1_out after "Aggr1.add((v10_1, v10_val))"
        # Begin maint Comp8 after "Aggr1.add((v10_1, v10_val))"
        _maint_Comp8_Aggr1_add((v10_1, v10_val))
        # End maint Comp8 after "Aggr1.add((v10_1, v10_val))"
        demand_Comp1(o)
        # End maint Aggr1 after "_U_Aggr1.add(o)"
    else:
        _U_Aggr1.incref(o)

def undemand_Aggr1(o):
    "sum(DEMQUERY(Comp1, [o], setmatch(Comp1, 'bu', o)), None)"
    if (_U_Aggr1.getref(o) == 1):
        # Begin maint Aggr1 before "_U_Aggr1.remove(o)"
        undemand_Comp1(o)
        v11_1 = o
        v11_elem = _m_Aggr1_out.singlelookup(o)
        # Begin maint Comp8 before "Aggr1.remove((v11_1, v11_elem))"
        _maint_Comp8_Aggr1_remove((v11_1, v11_elem))
        # End maint Comp8 before "Aggr1.remove((v11_1, v11_elem))"
        # Begin maint _m_Aggr1_out before "Aggr1.remove((v11_1, v11_elem))"
        _maint__m_Aggr1_out_remove((v11_1, v11_elem))
        # End maint _m_Aggr1_out before "Aggr1.remove((v11_1, v11_elem))"
        # End maint Aggr1 before "_U_Aggr1.remove(o)"
        _U_Aggr1.remove(o)
    else:
        _U_Aggr1.decref(o)

def query_Aggr1(o):
    "sum(DEMQUERY(Comp1, [o], setmatch(Comp1, 'bu', o)), None)"
    if (o not in _UEXT_Aggr1):
        _UEXT_Aggr1.add(o)
        demand_Aggr1(o)
    return True

Comp1 = RCSet()
def _maint_Comp1__U_Comp1_add(_e):
    # Iterate {(v2_o, v2_o_f, v2__e) : v2_o in deltamatch(_U_Comp1, 'b', _e, 1), (v2_o, v2_o_f) in _F_f, (v2_o_f, v2__e) in _M}
    v2_o = _e
    if hasattr(v2_o, 'f'):
        v2_o_f = v2_o.f
        if isinstance(v2_o_f, Set):
            for v2__e in v2_o_f:
                if ((v2_o, v2__e) not in Comp1):
                    Comp1.add((v2_o, v2__e))
                    # Begin maint _m_Comp1_out after "Comp1.add((v2_o, v2__e))"
                    _maint__m_Comp1_out_add((v2_o, v2__e))
                    # End maint _m_Comp1_out after "Comp1.add((v2_o, v2__e))"
                    # Begin maint Aggr1 after "Comp1.add((v2_o, v2__e))"
                    _maint_Aggr1_add((v2_o, v2__e))
                    # End maint Aggr1 after "Comp1.add((v2_o, v2__e))"
                else:
                    Comp1.incref((v2_o, v2__e))

def _maint_Comp1__U_Comp1_remove(_e):
    # Iterate {(v3_o, v3_o_f, v3__e) : v3_o in deltamatch(_U_Comp1, 'b', _e, 1), (v3_o, v3_o_f) in _F_f, (v3_o_f, v3__e) in _M}
    v3_o = _e
    if hasattr(v3_o, 'f'):
        v3_o_f = v3_o.f
        if isinstance(v3_o_f, Set):
            for v3__e in v3_o_f:
                if (Comp1.getref((v3_o, v3__e)) == 1):
                    # Begin maint Aggr1 before "Comp1.remove((v3_o, v3__e))"
                    _maint_Aggr1_remove((v3_o, v3__e))
                    # End maint Aggr1 before "Comp1.remove((v3_o, v3__e))"
                    # Begin maint _m_Comp1_out before "Comp1.remove((v3_o, v3__e))"
                    _maint__m_Comp1_out_remove((v3_o, v3__e))
                    # End maint _m_Comp1_out before "Comp1.remove((v3_o, v3__e))"
                    Comp1.remove((v3_o, v3__e))
                else:
                    Comp1.decref((v3_o, v3__e))

def _maint_Comp1__F_f_add(_e):
    # Iterate {(v4_o, v4_o_f, v4__e) : v4_o in _U_Comp1, (v4_o, v4_o_f) in deltamatch(_F_f, 'bb', _e, 1), (v4_o_f, v4__e) in _M}
    (v4_o, v4_o_f) = _e
    if (v4_o in _U_Comp1):
        if isinstance(v4_o_f, Set):
            for v4__e in v4_o_f:
                if ((v4_o, v4__e) not in Comp1):
                    Comp1.add((v4_o, v4__e))
                    # Begin maint _m_Comp1_out after "Comp1.add((v4_o, v4__e))"
                    _maint__m_Comp1_out_add((v4_o, v4__e))
                    # End maint _m_Comp1_out after "Comp1.add((v4_o, v4__e))"
                    # Begin maint Aggr1 after "Comp1.add((v4_o, v4__e))"
                    _maint_Aggr1_add((v4_o, v4__e))
                    # End maint Aggr1 after "Comp1.add((v4_o, v4__e))"
                else:
                    Comp1.incref((v4_o, v4__e))

def _maint_Comp1__M_add(_e):
    # Iterate {(v6_o, v6_o_f, v6__e) : v6_o in _U_Comp1, (v6_o, v6_o_f) in _F_f, (v6_o_f, v6__e) in deltamatch(_M, 'bb', _e, 1)}
    (v6_o_f, v6__e) = _e
    for v6_o in (_m__F_f_in[v6_o_f] if (v6_o_f in _m__F_f_in) else set()):
        if (v6_o in _U_Comp1):
            if ((v6_o, v6__e) not in Comp1):
                Comp1.add((v6_o, v6__e))
                # Begin maint _m_Comp1_out after "Comp1.add((v6_o, v6__e))"
                _maint__m_Comp1_out_add((v6_o, v6__e))
                # End maint _m_Comp1_out after "Comp1.add((v6_o, v6__e))"
                # Begin maint Aggr1 after "Comp1.add((v6_o, v6__e))"
                _maint_Aggr1_add((v6_o, v6__e))
                # End maint Aggr1 after "Comp1.add((v6_o, v6__e))"
            else:
                Comp1.incref((v6_o, v6__e))

_U_Comp1 = RCSet()
_UEXT_Comp1 = Set()
def demand_Comp1(o):
    '{(o, _e) : o in _U_Comp1, (o, o_f) in _F_f, (o_f, _e) in _M}'
    if (o not in _U_Comp1):
        _U_Comp1.add(o)
        # Begin maint Comp1 after "_U_Comp1.add(o)"
        _maint_Comp1__U_Comp1_add(o)
        # End maint Comp1 after "_U_Comp1.add(o)"
    else:
        _U_Comp1.incref(o)

def undemand_Comp1(o):
    '{(o, _e) : o in _U_Comp1, (o, o_f) in _F_f, (o_f, _e) in _M}'
    if (_U_Comp1.getref(o) == 1):
        # Begin maint Comp1 before "_U_Comp1.remove(o)"
        _maint_Comp1__U_Comp1_remove(o)
        # End maint Comp1 before "_U_Comp1.remove(o)"
        _U_Comp1.remove(o)
    else:
        _U_Comp1.decref(o)

def query_Comp1(o):
    '{(o, _e) : o in _U_Comp1, (o, o_f) in _F_f, (o_f, _e) in _M}'
    if (o not in _UEXT_Comp1):
        _UEXT_Comp1.add(o)
        demand_Comp1(o)
    return True

s = Set()
for x in [1, 2, 3]:
    o = Obj()
    o.f = Set()
    # Begin maint _m__F_f_in after "_F_f.add((o, Set()))"
    _maint__m__F_f_in_add((o, Set()))
    # End maint _m__F_f_in after "_F_f.add((o, Set()))"
    # Begin maint Comp1 after "_F_f.add((o, Set()))"
    _maint_Comp1__F_f_add((o, Set()))
    # End maint Comp1 after "_F_f.add((o, Set()))"
    for y in [10, 20, 30]:
        v1 = o.f
        v1.add((x * y))
        # Begin maint Comp8_d_M after "_M.add((v1, (x * y)))"
        _maint_Comp8_d_M__M_add((v1, (x * y)))
        # End maint Comp8_d_M after "_M.add((v1, (x * y)))"
        # Begin maint Comp8 after "_M.add((v1, (x * y)))"
        _maint_Comp8__M_add((v1, (x * y)))
        # End maint Comp8 after "_M.add((v1, (x * y)))"
        # Begin maint Comp1 after "_M.add((v1, (x * y)))"
        _maint_Comp1__M_add((v1, (x * y)))
        # End maint Comp1 after "_M.add((v1, (x * y)))"
        # Begin maint demand_Aggr1 after "_M.add((v1, (x * y)))"
        for v30_o in Aggr1_delta.elements():
            demand_Aggr1(v30_o)
        Aggr1_delta.clear()
        # End maint demand_Aggr1 after "_M.add((v1, (x * y)))"
    s.add(o)
    # Begin maint Comp8_d_M after "_M.add((s, o))"
    _maint_Comp8_d_M__M_add((s, o))
    # End maint Comp8_d_M after "_M.add((s, o))"
    # Begin maint Comp8 after "_M.add((s, o))"
    _maint_Comp8__M_add((s, o))
    # End maint Comp8 after "_M.add((s, o))"
    # Begin maint Comp1 after "_M.add((s, o))"
    _maint_Comp1__M_add((s, o))
    # End maint Comp1 after "_M.add((s, o))"
    # Begin maint demand_Aggr1 after "_M.add((s, o))"
    for v31_o in Aggr1_delta.elements():
        demand_Aggr1(v31_o)
    Aggr1_delta.clear()
    # End maint demand_Aggr1 after "_M.add((s, o))"
print(sorted((query_Comp8(s) and (_m_Comp8_out[s] if (s in _m_Comp8_out) else set()))))