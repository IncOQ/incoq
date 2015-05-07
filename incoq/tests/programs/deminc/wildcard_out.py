from incoq.runtime import *
# Comp1 := {(a, b) : _ in _U_Comp1, (a, b) in R, (b, _) in R}
# Comp1_Tb1 := {b : (a, b) in R}
# Comp1_dR2 := {(b, _v1) : b in Comp1_Tb1, (b, _v1) in R}
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

_m_R_in = Map()
def _maint__m_R_in_add(_e):
    (v19_1, v19_2) = _e
    if (v19_2 not in _m_R_in):
        _m_R_in[v19_2] = set()
    _m_R_in[v19_2].add(v19_1)

_m_Comp1_dR2_bw = Map()
def _maint__m_Comp1_dR2_bw_add(_e):
    (v17_1, v17_2) = _e
    if (v17_1 not in _m_Comp1_dR2_bw):
        _m_Comp1_dR2_bw[v17_1] = RCSet()
    if (() not in _m_Comp1_dR2_bw[v17_1]):
        _m_Comp1_dR2_bw[v17_1].add(())
    else:
        _m_Comp1_dR2_bw[v17_1].incref(())

def _maint__m_Comp1_dR2_bw_remove(_e):
    (v18_1, v18_2) = _e
    if (_m_Comp1_dR2_bw[v18_1].getref(()) == 1):
        _m_Comp1_dR2_bw[v18_1].remove(())
    else:
        _m_Comp1_dR2_bw[v18_1].decref(())
    if (len(_m_Comp1_dR2_bw[v18_1]) == 0):
        del _m_Comp1_dR2_bw[v18_1]

_m_R_bw = Map()
def _maint__m_R_bw_add(_e):
    (v15_1, v15_2) = _e
    if (v15_1 not in _m_R_bw):
        _m_R_bw[v15_1] = RCSet()
    if (() not in _m_R_bw[v15_1]):
        _m_R_bw[v15_1].add(())
    else:
        _m_R_bw[v15_1].incref(())

_m__U_Comp1_w = Map()
def _maint__m__U_Comp1_w_add(_e):
    if (() not in _m__U_Comp1_w):
        _m__U_Comp1_w[()] = RCSet()
    if (() not in _m__U_Comp1_w[()]):
        _m__U_Comp1_w[()].add(())
    else:
        _m__U_Comp1_w[()].incref(())

def _maint__m__U_Comp1_w_remove(_e):
    if (_m__U_Comp1_w[()].getref(()) == 1):
        _m__U_Comp1_w[()].remove(())
    else:
        _m__U_Comp1_w[()].decref(())
    if (len(_m__U_Comp1_w[()]) == 0):
        del _m__U_Comp1_w[()]

_m_R_out = Map()
def _maint__m_R_out_add(_e):
    (v11_1, v11_2) = _e
    if (v11_1 not in _m_R_out):
        _m_R_out[v11_1] = set()
    _m_R_out[v11_1].add(v11_2)

def _maint_Comp1_dR2_Comp1_Tb1_add(_e):
    # Iterate {(v7_b, v7__v1) : v7_b in deltamatch(Comp1_Tb1, 'b', _e, 1), (v7_b, v7__v1) in R}
    v7_b = _e
    for v7__v1 in (_m_R_out[v7_b] if (v7_b in _m_R_out) else set()):
        # Begin maint _m_Comp1_dR2_bw after "Comp1_dR2.add((v7_b, v7__v1))"
        _maint__m_Comp1_dR2_bw_add((v7_b, v7__v1))
        # End maint _m_Comp1_dR2_bw after "Comp1_dR2.add((v7_b, v7__v1))"

def _maint_Comp1_dR2_Comp1_Tb1_remove(_e):
    # Iterate {(v8_b, v8__v1) : v8_b in deltamatch(Comp1_Tb1, 'b', _e, 1), (v8_b, v8__v1) in R}
    v8_b = _e
    for v8__v1 in (_m_R_out[v8_b] if (v8_b in _m_R_out) else set()):
        # Begin maint _m_Comp1_dR2_bw before "Comp1_dR2.remove((v8_b, v8__v1))"
        _maint__m_Comp1_dR2_bw_remove((v8_b, v8__v1))
        # End maint _m_Comp1_dR2_bw before "Comp1_dR2.remove((v8_b, v8__v1))"

def _maint_Comp1_dR2_R_add(_e):
    # Iterate {(v9_b, v9__v1) : v9_b in Comp1_Tb1, (v9_b, v9__v1) in deltamatch(R, 'bb', _e, 1)}
    (v9_b, v9__v1) = _e
    if (v9_b in Comp1_Tb1):
        # Begin maint _m_Comp1_dR2_bw after "Comp1_dR2.add((v9_b, v9__v1))"
        _maint__m_Comp1_dR2_bw_add((v9_b, v9__v1))
        # End maint _m_Comp1_dR2_bw after "Comp1_dR2.add((v9_b, v9__v1))"

Comp1_Tb1 = RCSet()
def _maint_Comp1_Tb1_R_add(_e):
    # Iterate {(v5_a, v5_b) : (v5_a, v5_b) in deltamatch(R, 'bb', _e, 1)}
    (v5_a, v5_b) = _e
    if (v5_b not in Comp1_Tb1):
        Comp1_Tb1.add(v5_b)
        # Begin maint Comp1_dR2 after "Comp1_Tb1.add(v5_b)"
        _maint_Comp1_dR2_Comp1_Tb1_add(v5_b)
        # End maint Comp1_dR2 after "Comp1_Tb1.add(v5_b)"
    else:
        Comp1_Tb1.incref(v5_b)

def _maint_Comp1__U_Comp1_add(_e):
    # Iterate {(v1_a, v1_b) : _ in deltamatch(_U_Comp1, 'w', _e, 1), (v1_a, v1_b) in R, (v1_b, _) in R}
    for _ in setmatch(({_e} if ((_m__U_Comp1_w[()] if (() in _m__U_Comp1_w) else RCSet()).getref(()) == 1) else {}), 'w', ()):
        for (v1_a, v1_b) in R:
            for _ in (_m_R_bw[v1_b] if (v1_b in _m_R_bw) else RCSet()):
                # Begin maint _m_Comp1_out after "Comp1.add((v1_a, v1_b))"
                _maint__m_Comp1_out_add((v1_a, v1_b))
                # End maint _m_Comp1_out after "Comp1.add((v1_a, v1_b))"

def _maint_Comp1__U_Comp1_remove(_e):
    # Iterate {(v2_a, v2_b) : _ in deltamatch(_U_Comp1, 'w', _e, 1), (v2_a, v2_b) in R, (v2_b, _) in R}
    for _ in setmatch(({_e} if ((_m__U_Comp1_w[()] if (() in _m__U_Comp1_w) else RCSet()).getref(()) == 1) else {}), 'w', ()):
        for (v2_a, v2_b) in R:
            for _ in (_m_R_bw[v2_b] if (v2_b in _m_R_bw) else RCSet()):
                # Begin maint _m_Comp1_out before "Comp1.remove((v2_a, v2_b))"
                _maint__m_Comp1_out_remove((v2_a, v2_b))
                # End maint _m_Comp1_out before "Comp1.remove((v2_a, v2_b))"

def _maint_Comp1_R_add(_e):
    v3_DAS = set()
    # Iterate {(v3_a, v3_b) : _ in _U_Comp1, (v3_a, v3_b) in deltamatch(R, 'bb', _e, 1), (v3_b, _) in R}
    (v3_a, v3_b) = _e
    for _ in (_m_R_bw[v3_b] if (v3_b in _m_R_bw) else RCSet()):
        for _ in (_m__U_Comp1_w[()] if (() in _m__U_Comp1_w) else RCSet()):
            if ((v3_a, v3_b) not in v3_DAS):
                v3_DAS.add((v3_a, v3_b))
    # Iterate {(v3_a, v3_b) : _ in _U_Comp1, (v3_a, v3_b) in R, (v3_b, _) in deltamatch(Comp1_dR2, 'bw', _e, 1), (v3_b, _) in Comp1_dR2}
    for v3_b in setmatch(({_e} if ((_m_Comp1_dR2_bw[_e[0]] if (_e[0] in _m_Comp1_dR2_bw) else RCSet()).getref(()) == 1) else {}), 'uw', ()):
        for v3_a in (_m_R_in[v3_b] if (v3_b in _m_R_in) else set()):
            for _ in (_m_Comp1_dR2_bw[v3_b] if (v3_b in _m_Comp1_dR2_bw) else RCSet()):
                for _ in (_m__U_Comp1_w[()] if (() in _m__U_Comp1_w) else RCSet()):
                    if ((v3_a, v3_b) not in v3_DAS):
                        v3_DAS.add((v3_a, v3_b))
    for (v3_a, v3_b) in v3_DAS:
        # Begin maint _m_Comp1_out after "Comp1.add((v3_a, v3_b))"
        _maint__m_Comp1_out_add((v3_a, v3_b))
        # End maint _m_Comp1_out after "Comp1.add((v3_a, v3_b))"
    del v3_DAS

_U_Comp1 = RCSet()
_UEXT_Comp1 = Set()
def demand_Comp1():
    '{(a, b) : _ in _U_Comp1, (a, b) in R, (b, _) in R}'
    if (() not in _U_Comp1):
        _U_Comp1.add(())
        # Begin maint _m__U_Comp1_w after "_U_Comp1.add(())"
        _maint__m__U_Comp1_w_add(())
        # End maint _m__U_Comp1_w after "_U_Comp1.add(())"
        # Begin maint Comp1 after "_U_Comp1.add(())"
        _maint_Comp1__U_Comp1_add(())
        # End maint Comp1 after "_U_Comp1.add(())"
    else:
        _U_Comp1.incref(())

def undemand_Comp1():
    '{(a, b) : _ in _U_Comp1, (a, b) in R, (b, _) in R}'
    if (_U_Comp1.getref(()) == 1):
        # Begin maint Comp1 before "_U_Comp1.remove(())"
        _maint_Comp1__U_Comp1_remove(())
        # End maint Comp1 before "_U_Comp1.remove(())"
        # Begin maint _m__U_Comp1_w before "_U_Comp1.remove(())"
        _maint__m__U_Comp1_w_remove(())
        # End maint _m__U_Comp1_w before "_U_Comp1.remove(())"
        _U_Comp1.remove(())
    else:
        _U_Comp1.decref(())

def query_Comp1():
    '{(a, b) : _ in _U_Comp1, (a, b) in R, (b, _) in R}'
    if (() not in _UEXT_Comp1):
        _UEXT_Comp1.add(())
        demand_Comp1()
    return True

R = Set()
for (x, y) in [(1, 2), (2, 3), (3, 4)]:
    R.add((x, y))
    # Begin maint _m_R_in after "R.add((x, y))"
    _maint__m_R_in_add((x, y))
    # End maint _m_R_in after "R.add((x, y))"
    # Begin maint _m_R_bw after "R.add((x, y))"
    _maint__m_R_bw_add((x, y))
    # End maint _m_R_bw after "R.add((x, y))"
    # Begin maint _m_R_out after "R.add((x, y))"
    _maint__m_R_out_add((x, y))
    # End maint _m_R_out after "R.add((x, y))"
    # Begin maint Comp1_dR2 after "R.add((x, y))"
    _maint_Comp1_dR2_R_add((x, y))
    # End maint Comp1_dR2 after "R.add((x, y))"
    # Begin maint Comp1_Tb1 after "R.add((x, y))"
    _maint_Comp1_Tb1_R_add((x, y))
    # End maint Comp1_Tb1 after "R.add((x, y))"
    # Begin maint Comp1 after "R.add((x, y))"
    _maint_Comp1_R_add((x, y))
    # End maint Comp1 after "R.add((x, y))"
a = 1
print(sorted((query_Comp1() and (_m_Comp1_out[a] if (a in _m_Comp1_out) else set()))))