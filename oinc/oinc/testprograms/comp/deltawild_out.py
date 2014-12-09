from runtimelib import *
# Comp1 := {(x, w) : (x, _, z) in S, (z, w) in T}
_m_S_uwb = Map()
def _maint__m_S_uwb_add(_e):
    (v9_1, v9_2, v9_3) = _e
    if (v9_3 not in _m_S_uwb):
        _m_S_uwb[v9_3] = RCSet()
    if (v9_1 not in _m_S_uwb[v9_3]):
        _m_S_uwb[v9_3].add(v9_1)
    else:
        _m_S_uwb[v9_3].incref(v9_1)

_m_T_out = Map()
def _maint__m_T_out_add(_e):
    (v7_1, v7_2) = _e
    if (v7_1 not in _m_T_out):
        _m_T_out[v7_1] = set()
    _m_T_out[v7_1].add(v7_2)

def _maint__m_T_out_remove(_e):
    (v8_1, v8_2) = _e
    _m_T_out[v8_1].remove(v8_2)
    if (len(_m_T_out[v8_1]) == 0):
        del _m_T_out[v8_1]

_m_S_bwb = Map()
def _maint__m_S_bwb_add(_e):
    (v5_1, v5_2, v5_3) = _e
    if ((v5_1, v5_3) not in _m_S_bwb):
        _m_S_bwb[(v5_1, v5_3)] = RCSet()
    if (() not in _m_S_bwb[(v5_1, v5_3)]):
        _m_S_bwb[(v5_1, v5_3)].add(())
    else:
        _m_S_bwb[(v5_1, v5_3)].incref(())

Comp1 = RCSet()
def _maint_Comp1_S_add(_e):
    # Iterate {(v1_x, v1_z, v1_w) : (v1_x, _, v1_z) in deltamatch(S, 'bwb', _e, 1), (v1_z, v1_w) in T}
    for (v1_x, v1_z) in setmatch(({_e} if ((_m_S_bwb[(_e[0], _e[2])] if ((_e[0], _e[2]) in _m_S_bwb) else RCSet()).getref(()) == 1) else {}), 'uwu', ()):
        for v1_w in (_m_T_out[v1_z] if (v1_z in _m_T_out) else set()):
            if ((v1_x, v1_w) not in Comp1):
                Comp1.add((v1_x, v1_w))
            else:
                Comp1.incref((v1_x, v1_w))

def _maint_Comp1_T_add(_e):
    # Iterate {(v3_x, v3_z, v3_w) : (v3_x, _, v3_z) in S, (v3_z, v3_w) in deltamatch(T, 'bb', _e, 1)}
    (v3_z, v3_w) = _e
    for v3_x in (_m_S_uwb[v3_z] if (v3_z in _m_S_uwb) else RCSet()):
        if ((v3_x, v3_w) not in Comp1):
            Comp1.add((v3_x, v3_w))
        else:
            Comp1.incref((v3_x, v3_w))

def _maint_Comp1_T_remove(_e):
    # Iterate {(v4_x, v4_z, v4_w) : (v4_x, _, v4_z) in S, (v4_z, v4_w) in deltamatch(T, 'bb', _e, 1)}
    (v4_z, v4_w) = _e
    for v4_x in (_m_S_uwb[v4_z] if (v4_z in _m_S_uwb) else RCSet()):
        if (Comp1.getref((v4_x, v4_w)) == 1):
            Comp1.remove((v4_x, v4_w))
        else:
            Comp1.decref((v4_x, v4_w))

for (v1, v2) in [(2, 4), (3, 5)]:
    # Begin maint _m_T_out after "T.add((v1, v2))"
    _maint__m_T_out_add((v1, v2))
    # End maint _m_T_out after "T.add((v1, v2))"
    # Begin maint Comp1 after "T.add((v1, v2))"
    _maint_Comp1_T_add((v1, v2))
    # End maint Comp1 after "T.add((v1, v2))"
for (v1, v2, v3) in [(1, 1, 2), (1, 2, 2), (1, 2, 3)]:
    # Begin maint _m_S_uwb after "S.add((v1, v2, v3))"
    _maint__m_S_uwb_add((v1, v2, v3))
    # End maint _m_S_uwb after "S.add((v1, v2, v3))"
    # Begin maint _m_S_bwb after "S.add((v1, v2, v3))"
    _maint__m_S_bwb_add((v1, v2, v3))
    # End maint _m_S_bwb after "S.add((v1, v2, v3))"
    # Begin maint Comp1 after "S.add((v1, v2, v3))"
    _maint_Comp1_S_add((v1, v2, v3))
    # End maint Comp1 after "S.add((v1, v2, v3))"
print(sorted(Comp1))
# Begin maint Comp1 before "T.remove((2, 4))"
_maint_Comp1_T_remove((2, 4))
# End maint Comp1 before "T.remove((2, 4))"
# Begin maint _m_T_out before "T.remove((2, 4))"
_maint__m_T_out_remove((2, 4))
# End maint _m_T_out before "T.remove((2, 4))"
print(sorted(Comp1))