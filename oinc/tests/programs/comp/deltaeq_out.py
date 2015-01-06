from oinc.runtime import *
# Comp1 := {(x, w) : (x, x, z) in S, (z, w) in T}
_m_S_u1b = Map()
def _maint__m_S_u1b_add(_e):
    (v7_1, v7_2, v7_3) = _e
    if ((v7_1 == v7_2)):
        if (v7_3 not in _m_S_u1b):
            _m_S_u1b[v7_3] = set()
        _m_S_u1b[v7_3].add(v7_1)

_m_T_out = Map()
def _maint__m_T_out_add(_e):
    (v5_1, v5_2) = _e
    if (v5_1 not in _m_T_out):
        _m_T_out[v5_1] = set()
    _m_T_out[v5_1].add(v5_2)

Comp1 = RCSet()
def _maint_Comp1_S_add(_e):
    # Iterate {(v1_x, v1_z, v1_w) : (v1_x, v1_x, v1_z) in deltamatch(S, 'b1b', _e, 1), (v1_z, v1_w) in T}
    for (v1_x, v1_z) in setmatch({_e}, 'u1u', ()):
        for v1_w in (_m_T_out[v1_z] if (v1_z in _m_T_out) else set()):
            if ((v1_x, v1_w) not in Comp1):
                Comp1.add((v1_x, v1_w))
            else:
                Comp1.incref((v1_x, v1_w))

def _maint_Comp1_T_add(_e):
    # Iterate {(v3_x, v3_z, v3_w) : (v3_x, v3_x, v3_z) in S, (v3_z, v3_w) in deltamatch(T, 'bb', _e, 1)}
    (v3_z, v3_w) = _e
    for v3_x in (_m_S_u1b[v3_z] if (v3_z in _m_S_u1b) else set()):
        if ((v3_x, v3_w) not in Comp1):
            Comp1.add((v3_x, v3_w))
        else:
            Comp1.incref((v3_x, v3_w))

for (v1, v2) in [(2, 4), (3, 5)]:
    # Begin maint _m_T_out after "T.add((v1, v2))"
    _maint__m_T_out_add((v1, v2))
    # End maint _m_T_out after "T.add((v1, v2))"
    # Begin maint Comp1 after "T.add((v1, v2))"
    _maint_Comp1_T_add((v1, v2))
    # End maint Comp1 after "T.add((v1, v2))"
for (v1, v2, v3) in [(1, 1, 2), (1, 2, 3)]:
    # Begin maint _m_S_u1b after "S.add((v1, v2, v3))"
    _maint__m_S_u1b_add((v1, v2, v3))
    # End maint _m_S_u1b after "S.add((v1, v2, v3))"
    # Begin maint Comp1 after "S.add((v1, v2, v3))"
    _maint_Comp1_S_add((v1, v2, v3))
    # End maint Comp1 after "S.add((v1, v2, v3))"
print(sorted(Comp1))