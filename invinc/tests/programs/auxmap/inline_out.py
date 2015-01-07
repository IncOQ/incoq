from invinc.runtime import *
_m_R_in = Map()
_m_R_out = Map()
R = Set()
for (x, y) in [(1, 2), (1, 3), (2, 3), (1, 4)]:
    R.add((x, y))
    # Begin maint _m_R_in after "R.add((x, y))"
    (v3_1, v3_2) = (x, y)
    if (v3_2 not in _m_R_in):
        _m_R_in[v3_2] = set()
    _m_R_in[v3_2].add(v3_1)
    # End maint _m_R_in after "R.add((x, y))"
    # Begin maint _m_R_out after "R.add((x, y))"
    (v1_1, v1_2) = (x, y)
    if (v1_1 not in _m_R_out):
        _m_R_out[v1_1] = set()
    _m_R_out[v1_1].add(v1_2)
    # End maint _m_R_out after "R.add((x, y))"
# Begin maint _m_R_out before "R.remove((1, 4))"
(v2_1, v2_2) = (1, 4)
_m_R_out[v2_1].remove(v2_2)
if (len(_m_R_out[v2_1]) == 0):
    del _m_R_out[v2_1]
# End maint _m_R_out before "R.remove((1, 4))"
# Begin maint _m_R_in before "R.remove((1, 4))"
(v4_1, v4_2) = (1, 4)
_m_R_in[v4_2].remove(v4_1)
if (len(_m_R_in[v4_2]) == 0):
    del _m_R_in[v4_2]
# End maint _m_R_in before "R.remove((1, 4))"
R.remove((1, 4))
print(sorted(R))
print(sorted((_m_R_out[1] if (1 in _m_R_out) else set())))
print(sorted((_m_R_in[2] if (2 in _m_R_in) else set())))