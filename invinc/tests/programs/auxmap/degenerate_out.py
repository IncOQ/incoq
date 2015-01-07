from invinc.runtime import *
_m_R_uu = Map()
def _maint__m_R_uu_add(_e):
    (v3_1, v3_2) = _e
    if (() not in _m_R_uu):
        _m_R_uu[()] = set()
    _m_R_uu[()].add((v3_1, v3_2))

def _maint__m_R_uu_remove(_e):
    (v4_1, v4_2) = _e
    _m_R_uu[()].remove((v4_1, v4_2))
    if (len(_m_R_uu[()]) == 0):
        del _m_R_uu[()]

_m_R_bb = Map()
def _maint__m_R_bb_add(_e):
    (v1_1, v1_2) = _e
    if ((v1_1, v1_2) not in _m_R_bb):
        _m_R_bb[(v1_1, v1_2)] = set()
    _m_R_bb[(v1_1, v1_2)].add(())

def _maint__m_R_bb_remove(_e):
    (v2_1, v2_2) = _e
    _m_R_bb[(v2_1, v2_2)].remove(())
    if (len(_m_R_bb[(v2_1, v2_2)]) == 0):
        del _m_R_bb[(v2_1, v2_2)]

for (x, y) in [(1, 2), (1, 3), (2, 3), (1, 4)]:
    # Begin maint _m_R_uu after "R.add((x, y))"
    _maint__m_R_uu_add((x, y))
    # End maint _m_R_uu after "R.add((x, y))"
    # Begin maint _m_R_bb after "R.add((x, y))"
    _maint__m_R_bb_add((x, y))
    # End maint _m_R_bb after "R.add((x, y))"
# Begin maint _m_R_bb before "R.remove((1, 4))"
_maint__m_R_bb_remove((1, 4))
# End maint _m_R_bb before "R.remove((1, 4))"
# Begin maint _m_R_uu before "R.remove((1, 4))"
_maint__m_R_uu_remove((1, 4))
# End maint _m_R_uu before "R.remove((1, 4))"
print(sorted((_m_R_bb[(1, 2)] if ((1, 2) in _m_R_bb) else set())))
print(sorted((_m_R_uu[()] if (() in _m_R_uu) else set())))