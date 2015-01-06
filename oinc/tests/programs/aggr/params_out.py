from oinc.runtime import *
# Aggr1 := sum(setmatch(R, 'bu', k), None)
_m_Aggr1_out = Map()
def _maint__m_Aggr1_out_add(_e):
    (v3_1, v3_2) = _e
    if (v3_1 not in _m_Aggr1_out):
        _m_Aggr1_out[v3_1] = set()
    _m_Aggr1_out[v3_1].add(v3_2)

def _maint__m_Aggr1_out_remove(_e):
    (v4_1, v4_2) = _e
    _m_Aggr1_out[v4_1].remove(v4_2)
    if (len(_m_Aggr1_out[v4_1]) == 0):
        del _m_Aggr1_out[v4_1]

def _maint_Aggr1_add(_e):
    (v1_v1, v1_v2) = _e
    v1_val = _m_Aggr1_out.singlelookup(v1_v1, (0, 0))
    (v1_state, v1_count) = v1_val
    v1_state = (v1_state + v1_v2)
    v1_val = (v1_state, (v1_count + 1))
    v1_1 = v1_v1
    if (not (len((_m_Aggr1_out[v1_v1] if (v1_v1 in _m_Aggr1_out) else set())) == 0)):
        v1_elem = _m_Aggr1_out.singlelookup(v1_v1)
        # Begin maint _m_Aggr1_out before "Aggr1.remove((v1_1, v1_elem))"
        _maint__m_Aggr1_out_remove((v1_1, v1_elem))
        # End maint _m_Aggr1_out before "Aggr1.remove((v1_1, v1_elem))"
    # Begin maint _m_Aggr1_out after "Aggr1.add((v1_1, v1_val))"
    _maint__m_Aggr1_out_add((v1_1, v1_val))
    # End maint _m_Aggr1_out after "Aggr1.add((v1_1, v1_val))"

def _maint_Aggr1_remove(_e):
    (v2_v1, v2_v2) = _e
    v2_val = _m_Aggr1_out.singlelookup(v2_v1)
    if (v2_val[1] == 1):
        v2_1 = v2_v1
        v2_elem = _m_Aggr1_out.singlelookup(v2_v1)
        # Begin maint _m_Aggr1_out before "Aggr1.remove((v2_1, v2_elem))"
        _maint__m_Aggr1_out_remove((v2_1, v2_elem))
        # End maint _m_Aggr1_out before "Aggr1.remove((v2_1, v2_elem))"
    else:
        (v2_state, v2_count) = v2_val
        v2_state = (v2_state - v2_v2)
        v2_val = (v2_state, (v2_count - 1))
        v2_1 = v2_v1
        v2_elem = _m_Aggr1_out.singlelookup(v2_v1)
        # Begin maint _m_Aggr1_out before "Aggr1.remove((v2_1, v2_elem))"
        _maint__m_Aggr1_out_remove((v2_1, v2_elem))
        # End maint _m_Aggr1_out before "Aggr1.remove((v2_1, v2_elem))"
        # Begin maint _m_Aggr1_out after "Aggr1.add((v2_1, v2_val))"
        _maint__m_Aggr1_out_add((v2_1, v2_val))
        # End maint _m_Aggr1_out after "Aggr1.add((v2_1, v2_val))"

for x in [('A', 1), ('A', 2), ('A', 3), ('B', 4), ('B', 5)]:
    # Begin maint Aggr1 after "R.add(x)"
    _maint_Aggr1_add(x)
    # End maint Aggr1 after "R.add(x)"
# Begin maint Aggr1 before "R.remove(('B', 5))"
_maint_Aggr1_remove(('B', 5))
# End maint Aggr1 before "R.remove(('B', 5))"
k = 'A'
print(_m_Aggr1_out.singlelookup(k, (0, 0))[0])