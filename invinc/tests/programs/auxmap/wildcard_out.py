from invinc.runtime import *
_m_P_uwb = Map()
def _maint__m_P_uwb_add(_e):
    (v1_1, v1_2, v1_3) = _e
    if (v1_3 not in _m_P_uwb):
        _m_P_uwb[v1_3] = RCSet()
    if (v1_1 not in _m_P_uwb[v1_3]):
        _m_P_uwb[v1_3].add(v1_1)
    else:
        _m_P_uwb[v1_3].incref(v1_1)

def _maint__m_P_uwb_remove(_e):
    (v2_1, v2_2, v2_3) = _e
    if (_m_P_uwb[v2_3].getref(v2_1) == 1):
        _m_P_uwb[v2_3].remove(v2_1)
    else:
        _m_P_uwb[v2_3].decref(v2_1)
    if (len(_m_P_uwb[v2_3]) == 0):
        del _m_P_uwb[v2_3]

for v in [(1, 1, 2), (1, 2, 2), (3, 4, 2), (5, 6, 7)]:
    # Begin maint _m_P_uwb after "P.add(v)"
    _maint__m_P_uwb_add(v)
    # End maint _m_P_uwb after "P.add(v)"
print(sorted((_m_P_uwb[2] if (2 in _m_P_uwb) else RCSet())))
# Begin maint _m_P_uwb before "P.remove((1, 1, 2))"
_maint__m_P_uwb_remove((1, 1, 2))
# End maint _m_P_uwb before "P.remove((1, 1, 2))"
print(sorted((_m_P_uwb[2] if (2 in _m_P_uwb) else RCSet())))
# Begin maint _m_P_uwb before "P.remove((1, 2, 2))"
_maint__m_P_uwb_remove((1, 2, 2))
# End maint _m_P_uwb before "P.remove((1, 2, 2))"
print(sorted((_m_P_uwb[2] if (2 in _m_P_uwb) else RCSet())))