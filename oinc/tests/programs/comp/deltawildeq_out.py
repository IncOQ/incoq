from oinc.runtime import *
# Comp1 := {(x, w) : (x, x, _) in S, (x, w) in T}
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

_m_S_b1w = Map()
def _maint__m_S_b1w_add(_e):
    (v5_1, v5_2, v5_3) = _e
    if ((v5_1 == v5_2)):
        if (v5_1 not in _m_S_b1w):
            _m_S_b1w[v5_1] = RCSet()
        if (() not in _m_S_b1w[v5_1]):
            _m_S_b1w[v5_1].add(())
        else:
            _m_S_b1w[v5_1].incref(())

Comp1 = RCSet()
def _maint_Comp1_S_add(_e):
    # Iterate {(v1_x, v1_w) : (v1_x, v1_x, _) in deltamatch(S, 'b1w', _e, 1), (v1_x, v1_w) in T}
    for v1_x in setmatch(({_e} if ((_m_S_b1w[_e[0]] if (_e[0] in _m_S_b1w) else RCSet()).getref(()) == 1) else {}), 'u1w', ()):
        for v1_w in (_m_T_out[v1_x] if (v1_x in _m_T_out) else set()):
            Comp1.add((v1_x, v1_w))

def _maint_Comp1_T_add(_e):
    # Iterate {(v3_x, v3_w) : (v3_x, v3_x, _) in S, (v3_x, v3_w) in deltamatch(T, 'bb', _e, 1)}
    (v3_x, v3_w) = _e
    for _ in (_m_S_b1w[v3_x] if (v3_x in _m_S_b1w) else RCSet()):
        Comp1.add((v3_x, v3_w))

def _maint_Comp1_T_remove(_e):
    # Iterate {(v4_x, v4_w) : (v4_x, v4_x, _) in S, (v4_x, v4_w) in deltamatch(T, 'bb', _e, 1)}
    (v4_x, v4_w) = _e
    for _ in (_m_S_b1w[v4_x] if (v4_x in _m_S_b1w) else RCSet()):
        Comp1.remove((v4_x, v4_w))

for (v1, v2) in [(1, 3)]:
    # Begin maint _m_T_out after "T.add((v1, v2))"
    _maint__m_T_out_add((v1, v2))
    # End maint _m_T_out after "T.add((v1, v2))"
    # Begin maint Comp1 after "T.add((v1, v2))"
    _maint_Comp1_T_add((v1, v2))
    # End maint Comp1 after "T.add((v1, v2))"
for (v1, v2, v3) in [(1, 2, 2), (1, 1, 2)]:
    # Begin maint _m_S_b1w after "S.add((v1, v2, v3))"
    _maint__m_S_b1w_add((v1, v2, v3))
    # End maint _m_S_b1w after "S.add((v1, v2, v3))"
    # Begin maint Comp1 after "S.add((v1, v2, v3))"
    _maint_Comp1_S_add((v1, v2, v3))
    # End maint Comp1 after "S.add((v1, v2, v3))"
print(sorted(Comp1))
# Begin maint Comp1 before "T.remove((1, 3))"
_maint_Comp1_T_remove((1, 3))
# End maint Comp1 before "T.remove((1, 3))"
# Begin maint _m_T_out before "T.remove((1, 3))"
_maint__m_T_out_remove((1, 3))
# End maint _m_T_out before "T.remove((1, 3))"
print(sorted(Comp1))