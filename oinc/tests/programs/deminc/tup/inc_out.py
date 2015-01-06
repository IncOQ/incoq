from oinc.runtime import *
# Comp1 := {(a, e) : _ in _U_Comp1, (a, _tup1) in R, (_tup1, b2, _) in _TUP2, (b2, _tup2) in R, (_tup2, _, e) in _TUP2}
# Comp1_T_tup1 := {_tup1 : (a, _tup1) in R}
# Comp1_d_TUP21 := {(_tup1, b2, _v1) : _tup1 in Comp1_T_tup1, (_tup1, b2, _v1) in _TUP2}
# Comp1_Tb21 := {b2 : (_tup1, b2, _) in Comp1_d_TUP21}
# Comp1_dR2 := {(b2, _tup2) : b2 in Comp1_Tb21, (b2, _tup2) in R}
# Comp1_T_tup2 := {_tup2 : (b2, _tup2) in Comp1_dR2}
# Comp1_d_TUP22 := {(_tup2, _v1, e) : _tup2 in Comp1_T_tup2, (_tup2, _v1, e) in _TUP2}
_m_Comp1_out = Map()
def _maint__m_Comp1_out_add(_e):
    (v41_1, v41_2) = _e
    if (v41_1 not in _m_Comp1_out):
        _m_Comp1_out[v41_1] = set()
    _m_Comp1_out[v41_1].add(v41_2)

def _maint__m_Comp1_out_remove(_e):
    (v42_1, v42_2) = _e
    _m_Comp1_out[v42_1].remove(v42_2)
    if (len(_m_Comp1_out[v42_1]) == 0):
        del _m_Comp1_out[v42_1]

_m_Comp1_dR2_in = Map()
def _maint__m_Comp1_dR2_in_add(_e):
    (v39_1, v39_2) = _e
    if (v39_2 not in _m_Comp1_dR2_in):
        _m_Comp1_dR2_in[v39_2] = set()
    _m_Comp1_dR2_in[v39_2].add(v39_1)

def _maint__m_Comp1_dR2_in_remove(_e):
    (v40_1, v40_2) = _e
    _m_Comp1_dR2_in[v40_2].remove(v40_1)
    if (len(_m_Comp1_dR2_in[v40_2]) == 0):
        del _m_Comp1_dR2_in[v40_2]

_m_Comp1_d_TUP22_bwb = Map()
def _maint__m_Comp1_d_TUP22_bwb_add(_e):
    (v37_1, v37_2, v37_3) = _e
    if ((v37_1, v37_3) not in _m_Comp1_d_TUP22_bwb):
        _m_Comp1_d_TUP22_bwb[(v37_1, v37_3)] = RCSet()
    if (() not in _m_Comp1_d_TUP22_bwb[(v37_1, v37_3)]):
        _m_Comp1_d_TUP22_bwb[(v37_1, v37_3)].add(())
    else:
        _m_Comp1_d_TUP22_bwb[(v37_1, v37_3)].incref(())

def _maint__m_Comp1_d_TUP22_bwb_remove(_e):
    (v38_1, v38_2, v38_3) = _e
    if (_m_Comp1_d_TUP22_bwb[(v38_1, v38_3)].getref(()) == 1):
        _m_Comp1_d_TUP22_bwb[(v38_1, v38_3)].remove(())
    else:
        _m_Comp1_d_TUP22_bwb[(v38_1, v38_3)].decref(())
    if (len(_m_Comp1_d_TUP22_bwb[(v38_1, v38_3)]) == 0):
        del _m_Comp1_d_TUP22_bwb[(v38_1, v38_3)]

_m_R_in = Map()
def _maint__m_R_in_add(_e):
    (v35_1, v35_2) = _e
    if (v35_2 not in _m_R_in):
        _m_R_in[v35_2] = set()
    _m_R_in[v35_2].add(v35_1)

_m_Comp1_d_TUP21_ubw = Map()
def _maint__m_Comp1_d_TUP21_ubw_add(_e):
    (v33_1, v33_2, v33_3) = _e
    if (v33_2 not in _m_Comp1_d_TUP21_ubw):
        _m_Comp1_d_TUP21_ubw[v33_2] = RCSet()
    if (v33_1 not in _m_Comp1_d_TUP21_ubw[v33_2]):
        _m_Comp1_d_TUP21_ubw[v33_2].add(v33_1)
    else:
        _m_Comp1_d_TUP21_ubw[v33_2].incref(v33_1)

def _maint__m_Comp1_d_TUP21_ubw_remove(_e):
    (v34_1, v34_2, v34_3) = _e
    if (_m_Comp1_d_TUP21_ubw[v34_2].getref(v34_1) == 1):
        _m_Comp1_d_TUP21_ubw[v34_2].remove(v34_1)
    else:
        _m_Comp1_d_TUP21_ubw[v34_2].decref(v34_1)
    if (len(_m_Comp1_d_TUP21_ubw[v34_2]) == 0):
        del _m_Comp1_d_TUP21_ubw[v34_2]

_m_Comp1_dR2_out = Map()
def _maint__m_Comp1_dR2_out_add(_e):
    (v31_1, v31_2) = _e
    if (v31_1 not in _m_Comp1_dR2_out):
        _m_Comp1_dR2_out[v31_1] = set()
    _m_Comp1_dR2_out[v31_1].add(v31_2)

def _maint__m_Comp1_dR2_out_remove(_e):
    (v32_1, v32_2) = _e
    _m_Comp1_dR2_out[v32_1].remove(v32_2)
    if (len(_m_Comp1_dR2_out[v32_1]) == 0):
        del _m_Comp1_dR2_out[v32_1]

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

_m_Comp1_d_TUP21_bbw = Map()
def _maint__m_Comp1_d_TUP21_bbw_add(_e):
    (v27_1, v27_2, v27_3) = _e
    if ((v27_1, v27_2) not in _m_Comp1_d_TUP21_bbw):
        _m_Comp1_d_TUP21_bbw[(v27_1, v27_2)] = RCSet()
    if (() not in _m_Comp1_d_TUP21_bbw[(v27_1, v27_2)]):
        _m_Comp1_d_TUP21_bbw[(v27_1, v27_2)].add(())
    else:
        _m_Comp1_d_TUP21_bbw[(v27_1, v27_2)].incref(())

def _maint__m_Comp1_d_TUP21_bbw_remove(_e):
    (v28_1, v28_2, v28_3) = _e
    if (_m_Comp1_d_TUP21_bbw[(v28_1, v28_2)].getref(()) == 1):
        _m_Comp1_d_TUP21_bbw[(v28_1, v28_2)].remove(())
    else:
        _m_Comp1_d_TUP21_bbw[(v28_1, v28_2)].decref(())
    if (len(_m_Comp1_d_TUP21_bbw[(v28_1, v28_2)]) == 0):
        del _m_Comp1_d_TUP21_bbw[(v28_1, v28_2)]

_m_R_out = Map()
def _maint__m_R_out_add(_e):
    (v25_1, v25_2) = _e
    if (v25_1 not in _m_R_out):
        _m_R_out[v25_1] = set()
    _m_R_out[v25_1].add(v25_2)

def _maint_Comp1_d_TUP22_Comp1_T_tup2_add(_e):
    # Iterate {(v21__tup2, v21__v1, v21_e) : v21__tup2 in deltamatch(Comp1_T_tup2, 'b', _e, 1), (v21__tup2, v21__v1, v21_e) in _TUP2}
    v21__tup2 = _e
    if (isinstance(v21__tup2, tuple) and (len(v21__tup2) == 2)):
        for (v21__v1, v21_e) in setmatch({(v21__tup2, v21__tup2[0], v21__tup2[1])}, 'buu', v21__tup2):
            # Begin maint _m_Comp1_d_TUP22_bwb after "Comp1_d_TUP22.add((v21__tup2, v21__v1, v21_e))"
            _maint__m_Comp1_d_TUP22_bwb_add((v21__tup2, v21__v1, v21_e))
            # End maint _m_Comp1_d_TUP22_bwb after "Comp1_d_TUP22.add((v21__tup2, v21__v1, v21_e))"

def _maint_Comp1_d_TUP22_Comp1_T_tup2_remove(_e):
    # Iterate {(v22__tup2, v22__v1, v22_e) : v22__tup2 in deltamatch(Comp1_T_tup2, 'b', _e, 1), (v22__tup2, v22__v1, v22_e) in _TUP2}
    v22__tup2 = _e
    if (isinstance(v22__tup2, tuple) and (len(v22__tup2) == 2)):
        for (v22__v1, v22_e) in setmatch({(v22__tup2, v22__tup2[0], v22__tup2[1])}, 'buu', v22__tup2):
            # Begin maint _m_Comp1_d_TUP22_bwb before "Comp1_d_TUP22.remove((v22__tup2, v22__v1, v22_e))"
            _maint__m_Comp1_d_TUP22_bwb_remove((v22__tup2, v22__v1, v22_e))
            # End maint _m_Comp1_d_TUP22_bwb before "Comp1_d_TUP22.remove((v22__tup2, v22__v1, v22_e))"

Comp1_T_tup2 = RCSet()
def _maint_Comp1_T_tup2_Comp1_dR2_add(_e):
    # Iterate {(v19_b2, v19__tup2) : (v19_b2, v19__tup2) in deltamatch(Comp1_dR2, 'bb', _e, 1)}
    (v19_b2, v19__tup2) = _e
    if (v19__tup2 not in Comp1_T_tup2):
        Comp1_T_tup2.add(v19__tup2)
        # Begin maint Comp1_d_TUP22 after "Comp1_T_tup2.add(v19__tup2)"
        _maint_Comp1_d_TUP22_Comp1_T_tup2_add(v19__tup2)
        # End maint Comp1_d_TUP22 after "Comp1_T_tup2.add(v19__tup2)"
    else:
        Comp1_T_tup2.incref(v19__tup2)

def _maint_Comp1_T_tup2_Comp1_dR2_remove(_e):
    # Iterate {(v20_b2, v20__tup2) : (v20_b2, v20__tup2) in deltamatch(Comp1_dR2, 'bb', _e, 1)}
    (v20_b2, v20__tup2) = _e
    if (Comp1_T_tup2.getref(v20__tup2) == 1):
        # Begin maint Comp1_d_TUP22 before "Comp1_T_tup2.remove(v20__tup2)"
        _maint_Comp1_d_TUP22_Comp1_T_tup2_remove(v20__tup2)
        # End maint Comp1_d_TUP22 before "Comp1_T_tup2.remove(v20__tup2)"
        Comp1_T_tup2.remove(v20__tup2)
    else:
        Comp1_T_tup2.decref(v20__tup2)

Comp1_dR2 = RCSet()
def _maint_Comp1_dR2_Comp1_Tb21_add(_e):
    # Iterate {(v15_b2, v15__tup2) : v15_b2 in deltamatch(Comp1_Tb21, 'b', _e, 1), (v15_b2, v15__tup2) in R}
    v15_b2 = _e
    for v15__tup2 in (_m_R_out[v15_b2] if (v15_b2 in _m_R_out) else set()):
        Comp1_dR2.add((v15_b2, v15__tup2))
        # Begin maint _m_Comp1_dR2_in after "Comp1_dR2.add((v15_b2, v15__tup2))"
        _maint__m_Comp1_dR2_in_add((v15_b2, v15__tup2))
        # End maint _m_Comp1_dR2_in after "Comp1_dR2.add((v15_b2, v15__tup2))"
        # Begin maint _m_Comp1_dR2_out after "Comp1_dR2.add((v15_b2, v15__tup2))"
        _maint__m_Comp1_dR2_out_add((v15_b2, v15__tup2))
        # End maint _m_Comp1_dR2_out after "Comp1_dR2.add((v15_b2, v15__tup2))"
        # Begin maint Comp1_T_tup2 after "Comp1_dR2.add((v15_b2, v15__tup2))"
        _maint_Comp1_T_tup2_Comp1_dR2_add((v15_b2, v15__tup2))
        # End maint Comp1_T_tup2 after "Comp1_dR2.add((v15_b2, v15__tup2))"

def _maint_Comp1_dR2_Comp1_Tb21_remove(_e):
    # Iterate {(v16_b2, v16__tup2) : v16_b2 in deltamatch(Comp1_Tb21, 'b', _e, 1), (v16_b2, v16__tup2) in R}
    v16_b2 = _e
    for v16__tup2 in (_m_R_out[v16_b2] if (v16_b2 in _m_R_out) else set()):
        # Begin maint Comp1_T_tup2 before "Comp1_dR2.remove((v16_b2, v16__tup2))"
        _maint_Comp1_T_tup2_Comp1_dR2_remove((v16_b2, v16__tup2))
        # End maint Comp1_T_tup2 before "Comp1_dR2.remove((v16_b2, v16__tup2))"
        # Begin maint _m_Comp1_dR2_out before "Comp1_dR2.remove((v16_b2, v16__tup2))"
        _maint__m_Comp1_dR2_out_remove((v16_b2, v16__tup2))
        # End maint _m_Comp1_dR2_out before "Comp1_dR2.remove((v16_b2, v16__tup2))"
        # Begin maint _m_Comp1_dR2_in before "Comp1_dR2.remove((v16_b2, v16__tup2))"
        _maint__m_Comp1_dR2_in_remove((v16_b2, v16__tup2))
        # End maint _m_Comp1_dR2_in before "Comp1_dR2.remove((v16_b2, v16__tup2))"
        Comp1_dR2.remove((v16_b2, v16__tup2))

def _maint_Comp1_dR2_R_add(_e):
    # Iterate {(v17_b2, v17__tup2) : v17_b2 in Comp1_Tb21, (v17_b2, v17__tup2) in deltamatch(R, 'bb', _e, 1)}
    (v17_b2, v17__tup2) = _e
    if (v17_b2 in Comp1_Tb21):
        Comp1_dR2.add((v17_b2, v17__tup2))
        # Begin maint _m_Comp1_dR2_in after "Comp1_dR2.add((v17_b2, v17__tup2))"
        _maint__m_Comp1_dR2_in_add((v17_b2, v17__tup2))
        # End maint _m_Comp1_dR2_in after "Comp1_dR2.add((v17_b2, v17__tup2))"
        # Begin maint _m_Comp1_dR2_out after "Comp1_dR2.add((v17_b2, v17__tup2))"
        _maint__m_Comp1_dR2_out_add((v17_b2, v17__tup2))
        # End maint _m_Comp1_dR2_out after "Comp1_dR2.add((v17_b2, v17__tup2))"
        # Begin maint Comp1_T_tup2 after "Comp1_dR2.add((v17_b2, v17__tup2))"
        _maint_Comp1_T_tup2_Comp1_dR2_add((v17_b2, v17__tup2))
        # End maint Comp1_T_tup2 after "Comp1_dR2.add((v17_b2, v17__tup2))"

Comp1_Tb21 = RCSet()
def _maint_Comp1_Tb21_Comp1_d_TUP21_add(_e):
    # Iterate {(v13__tup1, v13_b2) : (v13__tup1, v13_b2, _) in deltamatch(Comp1_d_TUP21, 'bbw', _e, 1)}
    for (v13__tup1, v13_b2) in setmatch(({_e} if ((_m_Comp1_d_TUP21_bbw[(_e[0], _e[1])] if ((_e[0], _e[1]) in _m_Comp1_d_TUP21_bbw) else RCSet()).getref(()) == 1) else {}), 'uuw', ()):
        if (v13_b2 not in Comp1_Tb21):
            Comp1_Tb21.add(v13_b2)
            # Begin maint Comp1_dR2 after "Comp1_Tb21.add(v13_b2)"
            _maint_Comp1_dR2_Comp1_Tb21_add(v13_b2)
            # End maint Comp1_dR2 after "Comp1_Tb21.add(v13_b2)"
        else:
            Comp1_Tb21.incref(v13_b2)

def _maint_Comp1_Tb21_Comp1_d_TUP21_remove(_e):
    # Iterate {(v14__tup1, v14_b2) : (v14__tup1, v14_b2, _) in deltamatch(Comp1_d_TUP21, 'bbw', _e, 1)}
    for (v14__tup1, v14_b2) in setmatch(({_e} if ((_m_Comp1_d_TUP21_bbw[(_e[0], _e[1])] if ((_e[0], _e[1]) in _m_Comp1_d_TUP21_bbw) else RCSet()).getref(()) == 1) else {}), 'uuw', ()):
        if (Comp1_Tb21.getref(v14_b2) == 1):
            # Begin maint Comp1_dR2 before "Comp1_Tb21.remove(v14_b2)"
            _maint_Comp1_dR2_Comp1_Tb21_remove(v14_b2)
            # End maint Comp1_dR2 before "Comp1_Tb21.remove(v14_b2)"
            Comp1_Tb21.remove(v14_b2)
        else:
            Comp1_Tb21.decref(v14_b2)

def _maint_Comp1_d_TUP21_Comp1_T_tup1_add(_e):
    # Iterate {(v9__tup1, v9_b2, v9__v1) : v9__tup1 in deltamatch(Comp1_T_tup1, 'b', _e, 1), (v9__tup1, v9_b2, v9__v1) in _TUP2}
    v9__tup1 = _e
    if (isinstance(v9__tup1, tuple) and (len(v9__tup1) == 2)):
        for (v9_b2, v9__v1) in setmatch({(v9__tup1, v9__tup1[0], v9__tup1[1])}, 'buu', v9__tup1):
            # Begin maint _m_Comp1_d_TUP21_ubw after "Comp1_d_TUP21.add((v9__tup1, v9_b2, v9__v1))"
            _maint__m_Comp1_d_TUP21_ubw_add((v9__tup1, v9_b2, v9__v1))
            # End maint _m_Comp1_d_TUP21_ubw after "Comp1_d_TUP21.add((v9__tup1, v9_b2, v9__v1))"
            # Begin maint _m_Comp1_d_TUP21_bbw after "Comp1_d_TUP21.add((v9__tup1, v9_b2, v9__v1))"
            _maint__m_Comp1_d_TUP21_bbw_add((v9__tup1, v9_b2, v9__v1))
            # End maint _m_Comp1_d_TUP21_bbw after "Comp1_d_TUP21.add((v9__tup1, v9_b2, v9__v1))"
            # Begin maint Comp1_Tb21 after "Comp1_d_TUP21.add((v9__tup1, v9_b2, v9__v1))"
            _maint_Comp1_Tb21_Comp1_d_TUP21_add((v9__tup1, v9_b2, v9__v1))
            # End maint Comp1_Tb21 after "Comp1_d_TUP21.add((v9__tup1, v9_b2, v9__v1))"

def _maint_Comp1_d_TUP21_Comp1_T_tup1_remove(_e):
    # Iterate {(v10__tup1, v10_b2, v10__v1) : v10__tup1 in deltamatch(Comp1_T_tup1, 'b', _e, 1), (v10__tup1, v10_b2, v10__v1) in _TUP2}
    v10__tup1 = _e
    if (isinstance(v10__tup1, tuple) and (len(v10__tup1) == 2)):
        for (v10_b2, v10__v1) in setmatch({(v10__tup1, v10__tup1[0], v10__tup1[1])}, 'buu', v10__tup1):
            # Begin maint Comp1_Tb21 before "Comp1_d_TUP21.remove((v10__tup1, v10_b2, v10__v1))"
            _maint_Comp1_Tb21_Comp1_d_TUP21_remove((v10__tup1, v10_b2, v10__v1))
            # End maint Comp1_Tb21 before "Comp1_d_TUP21.remove((v10__tup1, v10_b2, v10__v1))"
            # Begin maint _m_Comp1_d_TUP21_bbw before "Comp1_d_TUP21.remove((v10__tup1, v10_b2, v10__v1))"
            _maint__m_Comp1_d_TUP21_bbw_remove((v10__tup1, v10_b2, v10__v1))
            # End maint _m_Comp1_d_TUP21_bbw before "Comp1_d_TUP21.remove((v10__tup1, v10_b2, v10__v1))"
            # Begin maint _m_Comp1_d_TUP21_ubw before "Comp1_d_TUP21.remove((v10__tup1, v10_b2, v10__v1))"
            _maint__m_Comp1_d_TUP21_ubw_remove((v10__tup1, v10_b2, v10__v1))
            # End maint _m_Comp1_d_TUP21_ubw before "Comp1_d_TUP21.remove((v10__tup1, v10_b2, v10__v1))"

Comp1_T_tup1 = RCSet()
def _maint_Comp1_T_tup1_R_add(_e):
    # Iterate {(v7_a, v7__tup1) : (v7_a, v7__tup1) in deltamatch(R, 'bb', _e, 1)}
    (v7_a, v7__tup1) = _e
    if (v7__tup1 not in Comp1_T_tup1):
        Comp1_T_tup1.add(v7__tup1)
        # Begin maint Comp1_d_TUP21 after "Comp1_T_tup1.add(v7__tup1)"
        _maint_Comp1_d_TUP21_Comp1_T_tup1_add(v7__tup1)
        # End maint Comp1_d_TUP21 after "Comp1_T_tup1.add(v7__tup1)"
    else:
        Comp1_T_tup1.incref(v7__tup1)

Comp1 = RCSet()
def _maint_Comp1__U_Comp1_add(_e):
    # Iterate {(v1_a, v1__tup1, v1_b2, v1__tup2, v1_e) : _ in deltamatch(_U_Comp1, 'w', _e, 1), (v1_a, v1__tup1) in R, (v1__tup1, v1_b2, _) in _TUP2, (v1_b2, v1__tup2) in Comp1_dR2, (v1__tup2, _, v1_e) in _TUP2}
    for _ in setmatch(({_e} if ((_m__U_Comp1_w[()] if (() in _m__U_Comp1_w) else RCSet()).getref(()) == 1) else {}), 'w', ()):
        for (v1_a, v1__tup1) in R:
            if (isinstance(v1__tup1, tuple) and (len(v1__tup1) == 2)):
                for v1_b2 in setmatch({(v1__tup1, v1__tup1[0], v1__tup1[1])}, 'buw', v1__tup1):
                    for v1__tup2 in (_m_Comp1_dR2_out[v1_b2] if (v1_b2 in _m_Comp1_dR2_out) else set()):
                        if (isinstance(v1__tup2, tuple) and (len(v1__tup2) == 2)):
                            for v1_e in setmatch({(v1__tup2, v1__tup2[0], v1__tup2[1])}, 'bwu', v1__tup2):
                                if ((v1_a, v1_e) not in Comp1):
                                    Comp1.add((v1_a, v1_e))
                                    # Begin maint _m_Comp1_out after "Comp1.add((v1_a, v1_e))"
                                    _maint__m_Comp1_out_add((v1_a, v1_e))
                                    # End maint _m_Comp1_out after "Comp1.add((v1_a, v1_e))"
                                else:
                                    Comp1.incref((v1_a, v1_e))

def _maint_Comp1__U_Comp1_remove(_e):
    # Iterate {(v2_a, v2__tup1, v2_b2, v2__tup2, v2_e) : _ in deltamatch(_U_Comp1, 'w', _e, 1), (v2_a, v2__tup1) in R, (v2__tup1, v2_b2, _) in _TUP2, (v2_b2, v2__tup2) in Comp1_dR2, (v2__tup2, _, v2_e) in _TUP2}
    for _ in setmatch(({_e} if ((_m__U_Comp1_w[()] if (() in _m__U_Comp1_w) else RCSet()).getref(()) == 1) else {}), 'w', ()):
        for (v2_a, v2__tup1) in R:
            if (isinstance(v2__tup1, tuple) and (len(v2__tup1) == 2)):
                for v2_b2 in setmatch({(v2__tup1, v2__tup1[0], v2__tup1[1])}, 'buw', v2__tup1):
                    for v2__tup2 in (_m_Comp1_dR2_out[v2_b2] if (v2_b2 in _m_Comp1_dR2_out) else set()):
                        if (isinstance(v2__tup2, tuple) and (len(v2__tup2) == 2)):
                            for v2_e in setmatch({(v2__tup2, v2__tup2[0], v2__tup2[1])}, 'bwu', v2__tup2):
                                if (Comp1.getref((v2_a, v2_e)) == 1):
                                    # Begin maint _m_Comp1_out before "Comp1.remove((v2_a, v2_e))"
                                    _maint__m_Comp1_out_remove((v2_a, v2_e))
                                    # End maint _m_Comp1_out before "Comp1.remove((v2_a, v2_e))"
                                    Comp1.remove((v2_a, v2_e))
                                else:
                                    Comp1.decref((v2_a, v2_e))

def _maint_Comp1_R_add(_e):
    v3_DAS = set()
    # Iterate {(v3_a, v3__tup1, v3_b2, v3__tup2, v3_e) : _ in _U_Comp1, (v3_a, v3__tup1) in deltamatch(R, 'bb', _e, 1), (v3__tup1, v3_b2, _) in _TUP2, (v3_b2, v3__tup2) in Comp1_dR2, (v3__tup2, _, v3_e) in _TUP2}
    (v3_a, v3__tup1) = _e
    if (isinstance(v3__tup1, tuple) and (len(v3__tup1) == 2)):
        for v3_b2 in setmatch({(v3__tup1, v3__tup1[0], v3__tup1[1])}, 'buw', v3__tup1):
            for v3__tup2 in (_m_Comp1_dR2_out[v3_b2] if (v3_b2 in _m_Comp1_dR2_out) else set()):
                if (isinstance(v3__tup2, tuple) and (len(v3__tup2) == 2)):
                    for v3_e in setmatch({(v3__tup2, v3__tup2[0], v3__tup2[1])}, 'bwu', v3__tup2):
                        for _ in (_m__U_Comp1_w[()] if (() in _m__U_Comp1_w) else RCSet()):
                            if ((v3_a, v3__tup1, v3_b2, v3__tup2, v3_e) not in v3_DAS):
                                v3_DAS.add((v3_a, v3__tup1, v3_b2, v3__tup2, v3_e))
    # Iterate {(v3_a, v3__tup1, v3_b2, v3__tup2, v3_e) : _ in _U_Comp1, (v3_a, v3__tup1) in R, (v3__tup1, v3_b2, _) in Comp1_d_TUP21, (v3_b2, v3__tup2) in deltamatch(Comp1_dR2, 'bb', _e, 1), (v3_b2, v3__tup2) in Comp1_dR2, (v3__tup2, _, v3_e) in _TUP2}
    (v3_b2, v3__tup2) = _e
    if ((v3_b2, v3__tup2) in Comp1_dR2):
        if (isinstance(v3__tup2, tuple) and (len(v3__tup2) == 2)):
            for v3_e in setmatch({(v3__tup2, v3__tup2[0], v3__tup2[1])}, 'bwu', v3__tup2):
                for v3__tup1 in (_m_Comp1_d_TUP21_ubw[v3_b2] if (v3_b2 in _m_Comp1_d_TUP21_ubw) else RCSet()):
                    for v3_a in (_m_R_in[v3__tup1] if (v3__tup1 in _m_R_in) else set()):
                        for _ in (_m__U_Comp1_w[()] if (() in _m__U_Comp1_w) else RCSet()):
                            if ((v3_a, v3__tup1, v3_b2, v3__tup2, v3_e) not in v3_DAS):
                                v3_DAS.add((v3_a, v3__tup1, v3_b2, v3__tup2, v3_e))
    for (v3_a, v3__tup1, v3_b2, v3__tup2, v3_e) in v3_DAS:
        if ((v3_a, v3_e) not in Comp1):
            Comp1.add((v3_a, v3_e))
            # Begin maint _m_Comp1_out after "Comp1.add((v3_a, v3_e))"
            _maint__m_Comp1_out_add((v3_a, v3_e))
            # End maint _m_Comp1_out after "Comp1.add((v3_a, v3_e))"
        else:
            Comp1.incref((v3_a, v3_e))
    del v3_DAS

_U_Comp1 = RCSet()
_UEXT_Comp1 = Set()
def demand_Comp1():
    '{(a, e) : _ in _U_Comp1, (a, _tup1) in R, (_tup1, b2, _) in _TUP2, (b2, _tup2) in R, (_tup2, _, e) in _TUP2}'
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
    '{(a, e) : _ in _U_Comp1, (a, _tup1) in R, (_tup1, b2, _) in _TUP2, (b2, _tup2) in R, (_tup2, _, e) in _TUP2}'
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
    '{(a, e) : _ in _U_Comp1, (a, _tup1) in R, (_tup1, b2, _) in _TUP2, (b2, _tup2) in R, (_tup2, _, e) in _TUP2}'
    if (() not in _UEXT_Comp1):
        _UEXT_Comp1.add(())
        demand_Comp1()
    return True

R = Set()
for (x, y) in [(1, (2, 3)), (2, (3, 4)), (3, (4, 5))]:
    R.add((x, y))
    # Begin maint _m_R_in after "R.add((x, y))"
    _maint__m_R_in_add((x, y))
    # End maint _m_R_in after "R.add((x, y))"
    # Begin maint _m_R_out after "R.add((x, y))"
    _maint__m_R_out_add((x, y))
    # End maint _m_R_out after "R.add((x, y))"
    # Begin maint Comp1_dR2 after "R.add((x, y))"
    _maint_Comp1_dR2_R_add((x, y))
    # End maint Comp1_dR2 after "R.add((x, y))"
    # Begin maint Comp1_T_tup1 after "R.add((x, y))"
    _maint_Comp1_T_tup1_R_add((x, y))
    # End maint Comp1_T_tup1 after "R.add((x, y))"
    # Begin maint Comp1 after "R.add((x, y))"
    _maint_Comp1_R_add((x, y))
    # End maint Comp1 after "R.add((x, y))"
a = 1
print(sorted((query_Comp1() and (_m_Comp1_out[a] if (a in _m_Comp1_out) else set()))))