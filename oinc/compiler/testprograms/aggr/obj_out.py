from runtimelib import *
# Comp1 := {(s, _e) : s in _U_Comp1, (s, _e) in _M}
# Comp1_Ts := {s : s in _U_Comp1}
# Comp1_d_M := {(s, _e) : s in Comp1_Ts, (s, _e) in _M}
# Aggr1 := sum(DEMQUERY(Comp1, [s], setmatch(Comp1, 'bu', s)), None)
# Comp12 := {(o, _e) : o in _U_Comp12, (o, o_f) in _F_f, (o_f, _e) in _M}
# Comp12_To := {o : o in _U_Comp12}
# Comp12_d_F_f := {(o, o_f) : o in Comp12_To, (o, o_f) in _F_f}
# Comp12_To_f := {o_f : (o, o_f) in Comp12_d_F_f}
# Comp12_d_M := {(o_f, _e) : o_f in Comp12_To_f, (o_f, _e) in _M}
# Aggr2 := sum(DEMQUERY(Comp12, [o], setmatch(Comp12, 'bu', o)), None)
_m_Comp1_out = Map()
def _maint__m_Comp1_out_add(_e):
    (v45_1, v45_2) = _e
    if (v45_1 not in _m_Comp1_out):
        _m_Comp1_out[v45_1] = set()
    _m_Comp1_out[v45_1].add(v45_2)

def _maint__m_Comp1_out_remove(_e):
    (v46_1, v46_2) = _e
    _m_Comp1_out[v46_1].remove(v46_2)
    if (len(_m_Comp1_out[v46_1]) == 0):
        del _m_Comp1_out[v46_1]

_m_Aggr1_out = Map()
def _maint__m_Aggr1_out_add(_e):
    (v43_1, v43_2) = _e
    if (v43_1 not in _m_Aggr1_out):
        _m_Aggr1_out[v43_1] = set()
    _m_Aggr1_out[v43_1].add(v43_2)

def _maint__m_Aggr1_out_remove(_e):
    (v44_1, v44_2) = _e
    _m_Aggr1_out[v44_1].remove(v44_2)
    if (len(_m_Aggr1_out[v44_1]) == 0):
        del _m_Aggr1_out[v44_1]

_m_Comp12_d_F_f_in = Map()
def _maint__m_Comp12_d_F_f_in_add(_e):
    (v41_1, v41_2) = _e
    if (v41_2 not in _m_Comp12_d_F_f_in):
        _m_Comp12_d_F_f_in[v41_2] = set()
    _m_Comp12_d_F_f_in[v41_2].add(v41_1)

def _maint__m_Comp12_d_F_f_in_remove(_e):
    (v42_1, v42_2) = _e
    _m_Comp12_d_F_f_in[v42_2].remove(v42_1)
    if (len(_m_Comp12_d_F_f_in[v42_2]) == 0):
        del _m_Comp12_d_F_f_in[v42_2]

_m_Comp12_out = Map()
def _maint__m_Comp12_out_add(_e):
    (v39_1, v39_2) = _e
    if (v39_1 not in _m_Comp12_out):
        _m_Comp12_out[v39_1] = set()
    _m_Comp12_out[v39_1].add(v39_2)

def _maint__m_Comp12_out_remove(_e):
    (v40_1, v40_2) = _e
    _m_Comp12_out[v40_1].remove(v40_2)
    if (len(_m_Comp12_out[v40_1]) == 0):
        del _m_Comp12_out[v40_1]

_m_Aggr2_out = Map()
def _maint__m_Aggr2_out_add(_e):
    (v37_1, v37_2) = _e
    if (v37_1 not in _m_Aggr2_out):
        _m_Aggr2_out[v37_1] = set()
    _m_Aggr2_out[v37_1].add(v37_2)

def _maint__m_Aggr2_out_remove(_e):
    (v38_1, v38_2) = _e
    _m_Aggr2_out[v38_1].remove(v38_2)
    if (len(_m_Aggr2_out[v38_1]) == 0):
        del _m_Aggr2_out[v38_1]

def _maint_Aggr2_add(_e):
    (v33_v1, v33_v2) = _e
    if (v33_v1 in _U_Aggr2):
        v33_val = _m_Aggr2_out.singlelookup(v33_v1)
        v33_val = (v33_val + v33_v2)
        v33_1 = v33_v1
        v33_elem = _m_Aggr2_out.singlelookup(v33_v1)
        # Begin maint _m_Aggr2_out before "Aggr2.remove((v33_1, v33_elem))"
        _maint__m_Aggr2_out_remove((v33_1, v33_elem))
        # End maint _m_Aggr2_out before "Aggr2.remove((v33_1, v33_elem))"
        # Begin maint _m_Aggr2_out after "Aggr2.add((v33_1, v33_val))"
        _maint__m_Aggr2_out_add((v33_1, v33_val))
        # End maint _m_Aggr2_out after "Aggr2.add((v33_1, v33_val))"

def _maint_Aggr2_remove(_e):
    (v34_v1, v34_v2) = _e
    if (v34_v1 in _U_Aggr2):
        v34_val = _m_Aggr2_out.singlelookup(v34_v1)
        v34_val = (v34_val - v34_v2)
        v34_1 = v34_v1
        v34_elem = _m_Aggr2_out.singlelookup(v34_v1)
        # Begin maint _m_Aggr2_out before "Aggr2.remove((v34_1, v34_elem))"
        _maint__m_Aggr2_out_remove((v34_1, v34_elem))
        # End maint _m_Aggr2_out before "Aggr2.remove((v34_1, v34_elem))"
        # Begin maint _m_Aggr2_out after "Aggr2.add((v34_1, v34_val))"
        _maint__m_Aggr2_out_add((v34_1, v34_val))
        # End maint _m_Aggr2_out after "Aggr2.add((v34_1, v34_val))"

_U_Aggr2 = RCSet()
_UEXT_Aggr2 = Set()
def demand_Aggr2(o):
    "sum(DEMQUERY(Comp12, [o], setmatch(Comp12, 'bu', o)), None)"
    if (o not in _U_Aggr2):
        _U_Aggr2.add(o)
        # Begin maint Aggr2 after "_U_Aggr2.add(o)"
        v35_val = 0
        for v35_elem in (_m_Comp12_out[o] if (o in _m_Comp12_out) else set()):
            v35_val = (v35_val + v35_elem)
        v35_1 = o
        # Begin maint _m_Aggr2_out after "Aggr2.add((v35_1, v35_val))"
        _maint__m_Aggr2_out_add((v35_1, v35_val))
        # End maint _m_Aggr2_out after "Aggr2.add((v35_1, v35_val))"
        demand_Comp12(o)
        # End maint Aggr2 after "_U_Aggr2.add(o)"
    else:
        _U_Aggr2.incref(o)

def undemand_Aggr2(o):
    "sum(DEMQUERY(Comp12, [o], setmatch(Comp12, 'bu', o)), None)"
    if (_U_Aggr2.getref(o) == 1):
        # Begin maint Aggr2 before "_U_Aggr2.remove(o)"
        undemand_Comp12(o)
        v36_1 = o
        v36_elem = _m_Aggr2_out.singlelookup(o)
        # Begin maint _m_Aggr2_out before "Aggr2.remove((v36_1, v36_elem))"
        _maint__m_Aggr2_out_remove((v36_1, v36_elem))
        # End maint _m_Aggr2_out before "Aggr2.remove((v36_1, v36_elem))"
        # End maint Aggr2 before "_U_Aggr2.remove(o)"
        _U_Aggr2.remove(o)
    else:
        _U_Aggr2.decref(o)

def query_Aggr2(o):
    "sum(DEMQUERY(Comp12, [o], setmatch(Comp12, 'bu', o)), None)"
    if (o not in _UEXT_Aggr2):
        _UEXT_Aggr2.add(o)
        demand_Aggr2(o)
    return True

Comp12_d_M = RCSet()
def _maint_Comp12_d_M_Comp12_To_f_add(_e):
    # Iterate {(v29_o_f, v29__e) : v29_o_f in deltamatch(Comp12_To_f, 'b', _e, 1), (v29_o_f, v29__e) in _M}
    v29_o_f = _e
    if isinstance(v29_o_f, Set):
        for v29__e in v29_o_f:
            Comp12_d_M.add((v29_o_f, v29__e))

def _maint_Comp12_d_M_Comp12_To_f_remove(_e):
    # Iterate {(v30_o_f, v30__e) : v30_o_f in deltamatch(Comp12_To_f, 'b', _e, 1), (v30_o_f, v30__e) in _M}
    v30_o_f = _e
    if isinstance(v30_o_f, Set):
        for v30__e in v30_o_f:
            Comp12_d_M.remove((v30_o_f, v30__e))

def _maint_Comp12_d_M__M_add(_e):
    # Iterate {(v31_o_f, v31__e) : v31_o_f in Comp12_To_f, (v31_o_f, v31__e) in deltamatch(_M, 'bb', _e, 1)}
    (v31_o_f, v31__e) = _e
    if (v31_o_f in Comp12_To_f):
        Comp12_d_M.add((v31_o_f, v31__e))

def _maint_Comp12_d_M__M_remove(_e):
    # Iterate {(v32_o_f, v32__e) : v32_o_f in Comp12_To_f, (v32_o_f, v32__e) in deltamatch(_M, 'bb', _e, 1)}
    (v32_o_f, v32__e) = _e
    if (v32_o_f in Comp12_To_f):
        Comp12_d_M.remove((v32_o_f, v32__e))

Comp12_To_f = RCSet()
def _maint_Comp12_To_f_Comp12_d_F_f_add(_e):
    # Iterate {(v27_o, v27_o_f) : (v27_o, v27_o_f) in deltamatch(Comp12_d_F_f, 'bb', _e, 1)}
    (v27_o, v27_o_f) = _e
    if (v27_o_f not in Comp12_To_f):
        Comp12_To_f.add(v27_o_f)
        # Begin maint Comp12_d_M after "Comp12_To_f.add(v27_o_f)"
        _maint_Comp12_d_M_Comp12_To_f_add(v27_o_f)
        # End maint Comp12_d_M after "Comp12_To_f.add(v27_o_f)"
    else:
        Comp12_To_f.incref(v27_o_f)

def _maint_Comp12_To_f_Comp12_d_F_f_remove(_e):
    # Iterate {(v28_o, v28_o_f) : (v28_o, v28_o_f) in deltamatch(Comp12_d_F_f, 'bb', _e, 1)}
    (v28_o, v28_o_f) = _e
    if (Comp12_To_f.getref(v28_o_f) == 1):
        # Begin maint Comp12_d_M before "Comp12_To_f.remove(v28_o_f)"
        _maint_Comp12_d_M_Comp12_To_f_remove(v28_o_f)
        # End maint Comp12_d_M before "Comp12_To_f.remove(v28_o_f)"
        Comp12_To_f.remove(v28_o_f)
    else:
        Comp12_To_f.decref(v28_o_f)

Comp12_d_F_f = RCSet()
def _maint_Comp12_d_F_f_Comp12_To_add(_e):
    # Iterate {(v23_o, v23_o_f) : v23_o in deltamatch(Comp12_To, 'b', _e, 1), (v23_o, v23_o_f) in _F_f}
    v23_o = _e
    if hasattr(v23_o, 'f'):
        v23_o_f = v23_o.f
        Comp12_d_F_f.add((v23_o, v23_o_f))
        # Begin maint _m_Comp12_d_F_f_in after "Comp12_d_F_f.add((v23_o, v23_o_f))"
        _maint__m_Comp12_d_F_f_in_add((v23_o, v23_o_f))
        # End maint _m_Comp12_d_F_f_in after "Comp12_d_F_f.add((v23_o, v23_o_f))"
        # Begin maint Comp12_To_f after "Comp12_d_F_f.add((v23_o, v23_o_f))"
        _maint_Comp12_To_f_Comp12_d_F_f_add((v23_o, v23_o_f))
        # End maint Comp12_To_f after "Comp12_d_F_f.add((v23_o, v23_o_f))"

def _maint_Comp12_d_F_f_Comp12_To_remove(_e):
    # Iterate {(v24_o, v24_o_f) : v24_o in deltamatch(Comp12_To, 'b', _e, 1), (v24_o, v24_o_f) in _F_f}
    v24_o = _e
    if hasattr(v24_o, 'f'):
        v24_o_f = v24_o.f
        # Begin maint Comp12_To_f before "Comp12_d_F_f.remove((v24_o, v24_o_f))"
        _maint_Comp12_To_f_Comp12_d_F_f_remove((v24_o, v24_o_f))
        # End maint Comp12_To_f before "Comp12_d_F_f.remove((v24_o, v24_o_f))"
        # Begin maint _m_Comp12_d_F_f_in before "Comp12_d_F_f.remove((v24_o, v24_o_f))"
        _maint__m_Comp12_d_F_f_in_remove((v24_o, v24_o_f))
        # End maint _m_Comp12_d_F_f_in before "Comp12_d_F_f.remove((v24_o, v24_o_f))"
        Comp12_d_F_f.remove((v24_o, v24_o_f))

def _maint_Comp12_d_F_f__F_f_add(_e):
    # Iterate {(v25_o, v25_o_f) : v25_o in Comp12_To, (v25_o, v25_o_f) in deltamatch(_F_f, 'bb', _e, 1)}
    (v25_o, v25_o_f) = _e
    if (v25_o in Comp12_To):
        Comp12_d_F_f.add((v25_o, v25_o_f))
        # Begin maint _m_Comp12_d_F_f_in after "Comp12_d_F_f.add((v25_o, v25_o_f))"
        _maint__m_Comp12_d_F_f_in_add((v25_o, v25_o_f))
        # End maint _m_Comp12_d_F_f_in after "Comp12_d_F_f.add((v25_o, v25_o_f))"
        # Begin maint Comp12_To_f after "Comp12_d_F_f.add((v25_o, v25_o_f))"
        _maint_Comp12_To_f_Comp12_d_F_f_add((v25_o, v25_o_f))
        # End maint Comp12_To_f after "Comp12_d_F_f.add((v25_o, v25_o_f))"

Comp12_To = RCSet()
def _maint_Comp12_To__U_Comp12_add(_e):
    # Iterate {v21_o : v21_o in deltamatch(_U_Comp12, 'b', _e, 1)}
    v21_o = _e
    Comp12_To.add(v21_o)
    # Begin maint Comp12_d_F_f after "Comp12_To.add(v21_o)"
    _maint_Comp12_d_F_f_Comp12_To_add(v21_o)
    # End maint Comp12_d_F_f after "Comp12_To.add(v21_o)"

def _maint_Comp12_To__U_Comp12_remove(_e):
    # Iterate {v22_o : v22_o in deltamatch(_U_Comp12, 'b', _e, 1)}
    v22_o = _e
    # Begin maint Comp12_d_F_f before "Comp12_To.remove(v22_o)"
    _maint_Comp12_d_F_f_Comp12_To_remove(v22_o)
    # End maint Comp12_d_F_f before "Comp12_To.remove(v22_o)"
    Comp12_To.remove(v22_o)

Comp12 = RCSet()
def _maint_Comp12__U_Comp12_add(_e):
    # Iterate {(v15_o, v15_o_f, v15__e) : v15_o in deltamatch(_U_Comp12, 'b', _e, 1), (v15_o, v15_o_f) in _F_f, (v15_o_f, v15__e) in _M}
    v15_o = _e
    if hasattr(v15_o, 'f'):
        v15_o_f = v15_o.f
        if isinstance(v15_o_f, Set):
            for v15__e in v15_o_f:
                if ((v15_o, v15__e) not in Comp12):
                    Comp12.add((v15_o, v15__e))
                    # Begin maint _m_Comp12_out after "Comp12.add((v15_o, v15__e))"
                    _maint__m_Comp12_out_add((v15_o, v15__e))
                    # End maint _m_Comp12_out after "Comp12.add((v15_o, v15__e))"
                    # Begin maint Aggr2 after "Comp12.add((v15_o, v15__e))"
                    _maint_Aggr2_add((v15_o, v15__e))
                    # End maint Aggr2 after "Comp12.add((v15_o, v15__e))"
                else:
                    Comp12.incref((v15_o, v15__e))

def _maint_Comp12__U_Comp12_remove(_e):
    # Iterate {(v16_o, v16_o_f, v16__e) : v16_o in deltamatch(_U_Comp12, 'b', _e, 1), (v16_o, v16_o_f) in _F_f, (v16_o_f, v16__e) in _M}
    v16_o = _e
    if hasattr(v16_o, 'f'):
        v16_o_f = v16_o.f
        if isinstance(v16_o_f, Set):
            for v16__e in v16_o_f:
                if (Comp12.getref((v16_o, v16__e)) == 1):
                    # Begin maint Aggr2 before "Comp12.remove((v16_o, v16__e))"
                    _maint_Aggr2_remove((v16_o, v16__e))
                    # End maint Aggr2 before "Comp12.remove((v16_o, v16__e))"
                    # Begin maint _m_Comp12_out before "Comp12.remove((v16_o, v16__e))"
                    _maint__m_Comp12_out_remove((v16_o, v16__e))
                    # End maint _m_Comp12_out before "Comp12.remove((v16_o, v16__e))"
                    Comp12.remove((v16_o, v16__e))
                else:
                    Comp12.decref((v16_o, v16__e))

def _maint_Comp12__F_f_add(_e):
    # Iterate {(v17_o, v17_o_f, v17__e) : v17_o in _U_Comp12, (v17_o, v17_o_f) in deltamatch(Comp12_d_F_f, 'bb', _e, 1), (v17_o, v17_o_f) in Comp12_d_F_f, (v17_o_f, v17__e) in _M}
    (v17_o, v17_o_f) = _e
    if (v17_o in _U_Comp12):
        if ((v17_o, v17_o_f) in Comp12_d_F_f):
            if isinstance(v17_o_f, Set):
                for v17__e in v17_o_f:
                    if ((v17_o, v17__e) not in Comp12):
                        Comp12.add((v17_o, v17__e))
                        # Begin maint _m_Comp12_out after "Comp12.add((v17_o, v17__e))"
                        _maint__m_Comp12_out_add((v17_o, v17__e))
                        # End maint _m_Comp12_out after "Comp12.add((v17_o, v17__e))"
                        # Begin maint Aggr2 after "Comp12.add((v17_o, v17__e))"
                        _maint_Aggr2_add((v17_o, v17__e))
                        # End maint Aggr2 after "Comp12.add((v17_o, v17__e))"
                    else:
                        Comp12.incref((v17_o, v17__e))

def _maint_Comp12__M_add(_e):
    # Iterate {(v19_o, v19_o_f, v19__e) : v19_o in _U_Comp12, (v19_o, v19_o_f) in Comp12_d_F_f, (v19_o_f, v19__e) in deltamatch(Comp12_d_M, 'bb', _e, 1), (v19_o_f, v19__e) in Comp12_d_M}
    (v19_o_f, v19__e) = _e
    if ((v19_o_f, v19__e) in Comp12_d_M):
        for v19_o in (_m_Comp12_d_F_f_in[v19_o_f] if (v19_o_f in _m_Comp12_d_F_f_in) else set()):
            if (v19_o in _U_Comp12):
                if ((v19_o, v19__e) not in Comp12):
                    Comp12.add((v19_o, v19__e))
                    # Begin maint _m_Comp12_out after "Comp12.add((v19_o, v19__e))"
                    _maint__m_Comp12_out_add((v19_o, v19__e))
                    # End maint _m_Comp12_out after "Comp12.add((v19_o, v19__e))"
                    # Begin maint Aggr2 after "Comp12.add((v19_o, v19__e))"
                    _maint_Aggr2_add((v19_o, v19__e))
                    # End maint Aggr2 after "Comp12.add((v19_o, v19__e))"
                else:
                    Comp12.incref((v19_o, v19__e))

def _maint_Comp12__M_remove(_e):
    # Iterate {(v20_o, v20_o_f, v20__e) : v20_o in _U_Comp12, (v20_o, v20_o_f) in Comp12_d_F_f, (v20_o_f, v20__e) in deltamatch(Comp12_d_M, 'bb', _e, 1), (v20_o_f, v20__e) in Comp12_d_M}
    (v20_o_f, v20__e) = _e
    if ((v20_o_f, v20__e) in Comp12_d_M):
        for v20_o in (_m_Comp12_d_F_f_in[v20_o_f] if (v20_o_f in _m_Comp12_d_F_f_in) else set()):
            if (v20_o in _U_Comp12):
                if (Comp12.getref((v20_o, v20__e)) == 1):
                    # Begin maint Aggr2 before "Comp12.remove((v20_o, v20__e))"
                    _maint_Aggr2_remove((v20_o, v20__e))
                    # End maint Aggr2 before "Comp12.remove((v20_o, v20__e))"
                    # Begin maint _m_Comp12_out before "Comp12.remove((v20_o, v20__e))"
                    _maint__m_Comp12_out_remove((v20_o, v20__e))
                    # End maint _m_Comp12_out before "Comp12.remove((v20_o, v20__e))"
                    Comp12.remove((v20_o, v20__e))
                else:
                    Comp12.decref((v20_o, v20__e))

_U_Comp12 = RCSet()
_UEXT_Comp12 = Set()
def demand_Comp12(o):
    '{(o, _e) : o in _U_Comp12, (o, o_f) in _F_f, (o_f, _e) in _M}'
    if (o not in _U_Comp12):
        _U_Comp12.add(o)
        # Begin maint Comp12_To after "_U_Comp12.add(o)"
        _maint_Comp12_To__U_Comp12_add(o)
        # End maint Comp12_To after "_U_Comp12.add(o)"
        # Begin maint Comp12 after "_U_Comp12.add(o)"
        _maint_Comp12__U_Comp12_add(o)
        # End maint Comp12 after "_U_Comp12.add(o)"
    else:
        _U_Comp12.incref(o)

def undemand_Comp12(o):
    '{(o, _e) : o in _U_Comp12, (o, o_f) in _F_f, (o_f, _e) in _M}'
    if (_U_Comp12.getref(o) == 1):
        # Begin maint Comp12 before "_U_Comp12.remove(o)"
        _maint_Comp12__U_Comp12_remove(o)
        # End maint Comp12 before "_U_Comp12.remove(o)"
        # Begin maint Comp12_To before "_U_Comp12.remove(o)"
        _maint_Comp12_To__U_Comp12_remove(o)
        # End maint Comp12_To before "_U_Comp12.remove(o)"
        _U_Comp12.remove(o)
    else:
        _U_Comp12.decref(o)

def query_Comp12(o):
    '{(o, _e) : o in _U_Comp12, (o, o_f) in _F_f, (o_f, _e) in _M}'
    if (o not in _UEXT_Comp12):
        _UEXT_Comp12.add(o)
        demand_Comp12(o)
    return True

def _maint_Aggr1_add(_e):
    (v11_v1, v11_v2) = _e
    if (v11_v1 in _U_Aggr1):
        v11_val = _m_Aggr1_out.singlelookup(v11_v1)
        v11_val = (v11_val + v11_v2)
        v11_1 = v11_v1
        v11_elem = _m_Aggr1_out.singlelookup(v11_v1)
        # Begin maint _m_Aggr1_out before "Aggr1.remove((v11_1, v11_elem))"
        _maint__m_Aggr1_out_remove((v11_1, v11_elem))
        # End maint _m_Aggr1_out before "Aggr1.remove((v11_1, v11_elem))"
        # Begin maint _m_Aggr1_out after "Aggr1.add((v11_1, v11_val))"
        _maint__m_Aggr1_out_add((v11_1, v11_val))
        # End maint _m_Aggr1_out after "Aggr1.add((v11_1, v11_val))"

def _maint_Aggr1_remove(_e):
    (v12_v1, v12_v2) = _e
    if (v12_v1 in _U_Aggr1):
        v12_val = _m_Aggr1_out.singlelookup(v12_v1)
        v12_val = (v12_val - v12_v2)
        v12_1 = v12_v1
        v12_elem = _m_Aggr1_out.singlelookup(v12_v1)
        # Begin maint _m_Aggr1_out before "Aggr1.remove((v12_1, v12_elem))"
        _maint__m_Aggr1_out_remove((v12_1, v12_elem))
        # End maint _m_Aggr1_out before "Aggr1.remove((v12_1, v12_elem))"
        # Begin maint _m_Aggr1_out after "Aggr1.add((v12_1, v12_val))"
        _maint__m_Aggr1_out_add((v12_1, v12_val))
        # End maint _m_Aggr1_out after "Aggr1.add((v12_1, v12_val))"

_U_Aggr1 = RCSet()
_UEXT_Aggr1 = Set()
def demand_Aggr1(s):
    "sum(DEMQUERY(Comp1, [s], setmatch(Comp1, 'bu', s)), None)"
    if (s not in _U_Aggr1):
        _U_Aggr1.add(s)
        # Begin maint Aggr1 after "_U_Aggr1.add(s)"
        v13_val = 0
        for v13_elem in (_m_Comp1_out[s] if (s in _m_Comp1_out) else set()):
            v13_val = (v13_val + v13_elem)
        v13_1 = s
        # Begin maint _m_Aggr1_out after "Aggr1.add((v13_1, v13_val))"
        _maint__m_Aggr1_out_add((v13_1, v13_val))
        # End maint _m_Aggr1_out after "Aggr1.add((v13_1, v13_val))"
        demand_Comp1(s)
        # End maint Aggr1 after "_U_Aggr1.add(s)"
    else:
        _U_Aggr1.incref(s)

def undemand_Aggr1(s):
    "sum(DEMQUERY(Comp1, [s], setmatch(Comp1, 'bu', s)), None)"
    if (_U_Aggr1.getref(s) == 1):
        # Begin maint Aggr1 before "_U_Aggr1.remove(s)"
        undemand_Comp1(s)
        v14_1 = s
        v14_elem = _m_Aggr1_out.singlelookup(s)
        # Begin maint _m_Aggr1_out before "Aggr1.remove((v14_1, v14_elem))"
        _maint__m_Aggr1_out_remove((v14_1, v14_elem))
        # End maint _m_Aggr1_out before "Aggr1.remove((v14_1, v14_elem))"
        # End maint Aggr1 before "_U_Aggr1.remove(s)"
        _U_Aggr1.remove(s)
    else:
        _U_Aggr1.decref(s)

def query_Aggr1(s):
    "sum(DEMQUERY(Comp1, [s], setmatch(Comp1, 'bu', s)), None)"
    if (s not in _UEXT_Aggr1):
        _UEXT_Aggr1.add(s)
        demand_Aggr1(s)
    return True

Comp1_d_M = RCSet()
def _maint_Comp1_d_M_Comp1_Ts_add(_e):
    # Iterate {(v7_s, v7__e) : v7_s in deltamatch(Comp1_Ts, 'b', _e, 1), (v7_s, v7__e) in _M}
    v7_s = _e
    if isinstance(v7_s, Set):
        for v7__e in v7_s:
            Comp1_d_M.add((v7_s, v7__e))

def _maint_Comp1_d_M_Comp1_Ts_remove(_e):
    # Iterate {(v8_s, v8__e) : v8_s in deltamatch(Comp1_Ts, 'b', _e, 1), (v8_s, v8__e) in _M}
    v8_s = _e
    if isinstance(v8_s, Set):
        for v8__e in v8_s:
            Comp1_d_M.remove((v8_s, v8__e))

def _maint_Comp1_d_M__M_add(_e):
    # Iterate {(v9_s, v9__e) : v9_s in Comp1_Ts, (v9_s, v9__e) in deltamatch(_M, 'bb', _e, 1)}
    (v9_s, v9__e) = _e
    if (v9_s in Comp1_Ts):
        Comp1_d_M.add((v9_s, v9__e))

def _maint_Comp1_d_M__M_remove(_e):
    # Iterate {(v10_s, v10__e) : v10_s in Comp1_Ts, (v10_s, v10__e) in deltamatch(_M, 'bb', _e, 1)}
    (v10_s, v10__e) = _e
    if (v10_s in Comp1_Ts):
        Comp1_d_M.remove((v10_s, v10__e))

Comp1_Ts = RCSet()
def _maint_Comp1_Ts__U_Comp1_add(_e):
    # Iterate {v5_s : v5_s in deltamatch(_U_Comp1, 'b', _e, 1)}
    v5_s = _e
    Comp1_Ts.add(v5_s)
    # Begin maint Comp1_d_M after "Comp1_Ts.add(v5_s)"
    _maint_Comp1_d_M_Comp1_Ts_add(v5_s)
    # End maint Comp1_d_M after "Comp1_Ts.add(v5_s)"

def _maint_Comp1_Ts__U_Comp1_remove(_e):
    # Iterate {v6_s : v6_s in deltamatch(_U_Comp1, 'b', _e, 1)}
    v6_s = _e
    # Begin maint Comp1_d_M before "Comp1_Ts.remove(v6_s)"
    _maint_Comp1_d_M_Comp1_Ts_remove(v6_s)
    # End maint Comp1_d_M before "Comp1_Ts.remove(v6_s)"
    Comp1_Ts.remove(v6_s)

def _maint_Comp1__U_Comp1_add(_e):
    # Iterate {(v1_s, v1__e) : v1_s in deltamatch(_U_Comp1, 'b', _e, 1), (v1_s, v1__e) in _M}
    v1_s = _e
    if isinstance(v1_s, Set):
        for v1__e in v1_s:
            # Begin maint _m_Comp1_out after "Comp1.add((v1_s, v1__e))"
            _maint__m_Comp1_out_add((v1_s, v1__e))
            # End maint _m_Comp1_out after "Comp1.add((v1_s, v1__e))"
            # Begin maint Aggr1 after "Comp1.add((v1_s, v1__e))"
            _maint_Aggr1_add((v1_s, v1__e))
            # End maint Aggr1 after "Comp1.add((v1_s, v1__e))"

def _maint_Comp1__U_Comp1_remove(_e):
    # Iterate {(v2_s, v2__e) : v2_s in deltamatch(_U_Comp1, 'b', _e, 1), (v2_s, v2__e) in _M}
    v2_s = _e
    if isinstance(v2_s, Set):
        for v2__e in v2_s:
            # Begin maint Aggr1 before "Comp1.remove((v2_s, v2__e))"
            _maint_Aggr1_remove((v2_s, v2__e))
            # End maint Aggr1 before "Comp1.remove((v2_s, v2__e))"
            # Begin maint _m_Comp1_out before "Comp1.remove((v2_s, v2__e))"
            _maint__m_Comp1_out_remove((v2_s, v2__e))
            # End maint _m_Comp1_out before "Comp1.remove((v2_s, v2__e))"

def _maint_Comp1__M_add(_e):
    # Iterate {(v3_s, v3__e) : v3_s in _U_Comp1, (v3_s, v3__e) in deltamatch(Comp1_d_M, 'bb', _e, 1), (v3_s, v3__e) in Comp1_d_M}
    (v3_s, v3__e) = _e
    if (v3_s in _U_Comp1):
        if ((v3_s, v3__e) in Comp1_d_M):
            # Begin maint _m_Comp1_out after "Comp1.add((v3_s, v3__e))"
            _maint__m_Comp1_out_add((v3_s, v3__e))
            # End maint _m_Comp1_out after "Comp1.add((v3_s, v3__e))"
            # Begin maint Aggr1 after "Comp1.add((v3_s, v3__e))"
            _maint_Aggr1_add((v3_s, v3__e))
            # End maint Aggr1 after "Comp1.add((v3_s, v3__e))"

def _maint_Comp1__M_remove(_e):
    # Iterate {(v4_s, v4__e) : v4_s in _U_Comp1, (v4_s, v4__e) in deltamatch(Comp1_d_M, 'bb', _e, 1), (v4_s, v4__e) in Comp1_d_M}
    (v4_s, v4__e) = _e
    if (v4_s in _U_Comp1):
        if ((v4_s, v4__e) in Comp1_d_M):
            # Begin maint Aggr1 before "Comp1.remove((v4_s, v4__e))"
            _maint_Aggr1_remove((v4_s, v4__e))
            # End maint Aggr1 before "Comp1.remove((v4_s, v4__e))"
            # Begin maint _m_Comp1_out before "Comp1.remove((v4_s, v4__e))"
            _maint__m_Comp1_out_remove((v4_s, v4__e))
            # End maint _m_Comp1_out before "Comp1.remove((v4_s, v4__e))"

_U_Comp1 = RCSet()
_UEXT_Comp1 = Set()
def demand_Comp1(s):
    '{(s, _e) : s in _U_Comp1, (s, _e) in _M}'
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
    '{(s, _e) : s in _U_Comp1, (s, _e) in _M}'
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
    '{(s, _e) : s in _U_Comp1, (s, _e) in _M}'
    if (s not in _UEXT_Comp1):
        _UEXT_Comp1.add(s)
        demand_Comp1(s)
    return True

r = Set()
t = Set()
o = Obj()
o.f = t
# Begin maint Comp12_d_F_f after "_F_f.add((o, t))"
_maint_Comp12_d_F_f__F_f_add((o, t))
# End maint Comp12_d_F_f after "_F_f.add((o, t))"
# Begin maint Comp12 after "_F_f.add((o, t))"
_maint_Comp12__F_f_add((o, t))
# End maint Comp12 after "_F_f.add((o, t))"
for x in [1, 2, 3, 4, 5]:
    r.add(x)
    # Begin maint Comp12_d_M after "_M.add((r, x))"
    _maint_Comp12_d_M__M_add((r, x))
    # End maint Comp12_d_M after "_M.add((r, x))"
    # Begin maint Comp12 after "_M.add((r, x))"
    _maint_Comp12__M_add((r, x))
    # End maint Comp12 after "_M.add((r, x))"
    # Begin maint Comp1_d_M after "_M.add((r, x))"
    _maint_Comp1_d_M__M_add((r, x))
    # End maint Comp1_d_M after "_M.add((r, x))"
    # Begin maint Comp1 after "_M.add((r, x))"
    _maint_Comp1__M_add((r, x))
    # End maint Comp1 after "_M.add((r, x))"
    t.add(x)
    # Begin maint Comp12_d_M after "_M.add((t, x))"
    _maint_Comp12_d_M__M_add((t, x))
    # End maint Comp12_d_M after "_M.add((t, x))"
    # Begin maint Comp12 after "_M.add((t, x))"
    _maint_Comp12__M_add((t, x))
    # End maint Comp12 after "_M.add((t, x))"
    # Begin maint Comp1_d_M after "_M.add((t, x))"
    _maint_Comp1_d_M__M_add((t, x))
    # End maint Comp1_d_M after "_M.add((t, x))"
    # Begin maint Comp1 after "_M.add((t, x))"
    _maint_Comp1__M_add((t, x))
    # End maint Comp1 after "_M.add((t, x))"
# Begin maint Comp1 before "_M.remove((r, 5))"
_maint_Comp1__M_remove((r, 5))
# End maint Comp1 before "_M.remove((r, 5))"
# Begin maint Comp1_d_M before "_M.remove((r, 5))"
_maint_Comp1_d_M__M_remove((r, 5))
# End maint Comp1_d_M before "_M.remove((r, 5))"
# Begin maint Comp12 before "_M.remove((r, 5))"
_maint_Comp12__M_remove((r, 5))
# End maint Comp12 before "_M.remove((r, 5))"
# Begin maint Comp12_d_M before "_M.remove((r, 5))"
_maint_Comp12_d_M__M_remove((r, 5))
# End maint Comp12_d_M before "_M.remove((r, 5))"
r.remove(5)
s = r
print((query_Aggr1(s) and _m_Aggr1_out.singlelookup(s)))
print((query_Aggr2(o) and _m_Aggr2_out.singlelookup(o)))