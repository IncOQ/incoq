from oinc.runtime import *
# Comp1 := {x : (x, x, y, _) in P, y in S}
_m_P_u1bw = Map()
def _maint__m_P_u1bw_add(_e):
    (v7_1, v7_2, v7_3, v7_4) = _e
    if ((v7_1 == v7_2)):
        if (v7_3 not in _m_P_u1bw):
            _m_P_u1bw[v7_3] = RCSet()
        if (v7_1 not in _m_P_u1bw[v7_3]):
            _m_P_u1bw[v7_3].add(v7_1)
        else:
            _m_P_u1bw[v7_3].incref(v7_1)

_m_P_b1bw = Map()
def _maint__m_P_b1bw_add(_e):
    (v5_1, v5_2, v5_3, v5_4) = _e
    if ((v5_1 == v5_2)):
        if ((v5_1, v5_3) not in _m_P_b1bw):
            _m_P_b1bw[(v5_1, v5_3)] = RCSet()
        if (() not in _m_P_b1bw[(v5_1, v5_3)]):
            _m_P_b1bw[(v5_1, v5_3)].add(())
        else:
            _m_P_b1bw[(v5_1, v5_3)].incref(())

Comp1 = RCSet()
def _maint_Comp1_P_add(_e):
    # Iterate {(v1_x, v1_y) : (v1_x, v1_x, v1_y, _) in deltamatch(P, 'b1bw', _e, 1), v1_y in S}
    for (v1_x, v1_y) in setmatch(({_e} if ((_m_P_b1bw[(_e[0], _e[2])] if ((_e[0], _e[2]) in _m_P_b1bw) else RCSet()).getref(()) == 1) else {}), 'u1uw', ()):
        if (v1_y in S):
            if (v1_x not in Comp1):
                Comp1.add(v1_x)
            else:
                Comp1.incref(v1_x)

def _maint_Comp1_S_add(_e):
    # Iterate {(v3_x, v3_y) : (v3_x, v3_x, v3_y, _) in P, v3_y in deltamatch(S, 'b', _e, 1)}
    v3_y = _e
    for v3_x in (_m_P_u1bw[v3_y] if (v3_y in _m_P_u1bw) else RCSet()):
        if (v3_x not in Comp1):
            Comp1.add(v3_x)
        else:
            Comp1.incref(v3_x)

S = Set()
for v in {(1, 1, 2, 3), (1, 2, 2, 4)}:
    # Begin maint _m_P_u1bw after "P.add(v)"
    _maint__m_P_u1bw_add(v)
    # End maint _m_P_u1bw after "P.add(v)"
    # Begin maint _m_P_b1bw after "P.add(v)"
    _maint__m_P_b1bw_add(v)
    # End maint _m_P_b1bw after "P.add(v)"
    # Begin maint Comp1 after "P.add(v)"
    _maint_Comp1_P_add(v)
    # End maint Comp1 after "P.add(v)"
S.add(2)
# Begin maint Comp1 after "S.add(2)"
_maint_Comp1_S_add(2)
# End maint Comp1 after "S.add(2)"
print(sorted(Comp1))