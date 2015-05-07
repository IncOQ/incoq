from incoq.runtime import *
# Comp1 := {z : (x, _, z) in R, x in S}
_m_R_bwu = Map()
def _maint__m_R_bwu_add(_e):
    (v8_1, v8_2, v8_3) = _e
    if (v8_1 not in _m_R_bwu):
        _m_R_bwu[v8_1] = RCSet()
    if (v8_3 not in _m_R_bwu[v8_1]):
        _m_R_bwu[v8_1].add(v8_3)
    else:
        _m_R_bwu[v8_1].incref(v8_3)

_m_R_bwb = Map()
def _maint__m_R_bwb_add(_e):
    (v6_1, v6_2, v6_3) = _e
    if ((v6_1, v6_3) not in _m_R_bwb):
        _m_R_bwb[(v6_1, v6_3)] = RCSet()
    if (() not in _m_R_bwb[(v6_1, v6_3)]):
        _m_R_bwb[(v6_1, v6_3)].add(())
    else:
        _m_R_bwb[(v6_1, v6_3)].incref(())

Comp1 = RCSet()
def _maint_Comp1_R_add(_e):
    # Iterate {(v2_x, v2_z) : (v2_x, _, v2_z) in deltamatch(R, 'bwb', _e, 1), v2_x in S}
    for (v2_x, v2_z) in setmatch(({_e} if ((_m_R_bwb[(_e[0], _e[2])] if ((_e[0], _e[2]) in _m_R_bwb) else RCSet()).getref(()) == 1) else {}), 'uwu', ()):
        if (v2_x in S):
            if (v2_z not in Comp1):
                Comp1.add(v2_z)
            else:
                Comp1.incref(v2_z)

def _maint_Comp1_S_add(_e):
    # Iterate {(v4_x, v4_z) : (v4_x, _, v4_z) in R, v4_x in deltamatch(S, 'b', _e, 1)}
    v4_x = _e
    for v4_z in (_m_R_bwu[v4_x] if (v4_x in _m_R_bwu) else RCSet()):
        if (v4_z not in Comp1):
            Comp1.add(v4_z)
        else:
            Comp1.incref(v4_z)

R = Set()
S = Set()
for _upelem in [(1, (2, 3)), (4, (5, 6))]:
    if (_upelem not in R):
        _ftv1 = (_upelem[0], _upelem[1][0], _upelem[1][1])
        R.add(_ftv1)
        # Begin maint _m_R_bwu after "R.add(_ftv1)"
        _maint__m_R_bwu_add(_ftv1)
        # End maint _m_R_bwu after "R.add(_ftv1)"
        # Begin maint _m_R_bwb after "R.add(_ftv1)"
        _maint__m_R_bwb_add(_ftv1)
        # End maint _m_R_bwb after "R.add(_ftv1)"
        # Begin maint Comp1 after "R.add(_ftv1)"
        _maint_Comp1_R_add(_ftv1)
        # End maint Comp1 after "R.add(_ftv1)"
for _upelem in [1, 4]:
    if (_upelem not in S):
        S.add(_upelem)
        # Begin maint Comp1 after "S.add(_upelem)"
        _maint_Comp1_S_add(_upelem)
        # End maint Comp1 after "S.add(_upelem)"
print(sorted(Comp1))