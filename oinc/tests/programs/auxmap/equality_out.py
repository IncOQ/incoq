from oinc.runtime import *
_m_P_ub2 = Map()
def _maint__m_P_ub2_add(_e):
    (v3_1, v3_2, v3_3) = _e
    if ((v3_2 == v3_3)):
        if (v3_2 not in _m_P_ub2):
            _m_P_ub2[v3_2] = set()
        _m_P_ub2[v3_2].add(v3_1)

def _maint__m_P_ub2_remove(_e):
    (v4_1, v4_2, v4_3) = _e
    if ((v4_2 == v4_3)):
        _m_P_ub2[v4_2].remove(v4_1)
        if (len(_m_P_ub2[v4_2]) == 0):
            del _m_P_ub2[v4_2]

_m_P_uu2 = Map()
def _maint__m_P_uu2_add(_e):
    (v1_1, v1_2, v1_3) = _e
    if ((v1_2 == v1_3)):
        if (() not in _m_P_uu2):
            _m_P_uu2[()] = set()
        _m_P_uu2[()].add((v1_1, v1_2))

def _maint__m_P_uu2_remove(_e):
    (v2_1, v2_2, v2_3) = _e
    if ((v2_2 == v2_3)):
        _m_P_uu2[()].remove((v2_1, v2_2))
        if (len(_m_P_uu2[()]) == 0):
            del _m_P_uu2[()]

for v in [(1, 2, 2), (2, 2, 2), (3, 3, 3), (4, 1, 2), (5, 2, 3), (9, 9, 9)]:
    # Begin maint _m_P_ub2 after "P.add(v)"
    _maint__m_P_ub2_add(v)
    # End maint _m_P_ub2 after "P.add(v)"
    # Begin maint _m_P_uu2 after "P.add(v)"
    _maint__m_P_uu2_add(v)
    # End maint _m_P_uu2 after "P.add(v)"
# Begin maint _m_P_uu2 before "P.remove((9, 9, 9))"
_maint__m_P_uu2_remove((9, 9, 9))
# End maint _m_P_uu2 before "P.remove((9, 9, 9))"
# Begin maint _m_P_ub2 before "P.remove((9, 9, 9))"
_maint__m_P_ub2_remove((9, 9, 9))
# End maint _m_P_ub2 before "P.remove((9, 9, 9))"
print(sorted((_m_P_uu2[()] if (() in _m_P_uu2) else set())))
print(sorted((_m_P_ub2[2] if (2 in _m_P_ub2) else set())))