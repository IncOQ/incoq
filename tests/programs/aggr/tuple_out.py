from incoq.runtime import *
# Aggr1 := count(R, None)
# Aggr2 := count(setmatch(R, 'buu', a), None)
_m_Aggr1_u = Map()
def _maint__m_Aggr1_u_add(_e):
    v7_1 = _e
    if (() not in _m_Aggr1_u):
        _m_Aggr1_u[()] = set()
    _m_Aggr1_u[()].add(v7_1)

def _maint__m_Aggr1_u_remove(_e):
    v8_1 = _e
    _m_Aggr1_u[()].remove(v8_1)
    if (len(_m_Aggr1_u[()]) == 0):
        del _m_Aggr1_u[()]

_m_Aggr2_out = Map()
def _maint__m_Aggr2_out_add(_e):
    (v5_1, v5_2) = _e
    if (v5_1 not in _m_Aggr2_out):
        _m_Aggr2_out[v5_1] = set()
    _m_Aggr2_out[v5_1].add(v5_2)

def _maint__m_Aggr2_out_remove(_e):
    (v6_1, v6_2) = _e
    _m_Aggr2_out[v6_1].remove(v6_2)
    if (len(_m_Aggr2_out[v6_1]) == 0):
        del _m_Aggr2_out[v6_1]

def _maint_Aggr2_add(_e):
    (v3_v1, v3_v2, v3_v3) = _e
    v3_val = _m_Aggr2_out.singlelookup(v3_v1, (0, 0))
    (v3_state, v3_count) = v3_val
    v3_state = (v3_state + 1)
    v3_val = (v3_state, (v3_count + 1))
    v3_1 = v3_v1
    if (not (len((_m_Aggr2_out[v3_v1] if (v3_v1 in _m_Aggr2_out) else set())) == 0)):
        v3_elem = _m_Aggr2_out.singlelookup(v3_v1)
        # Begin maint _m_Aggr2_out before "Aggr2.remove((v3_1, v3_elem))"
        _maint__m_Aggr2_out_remove((v3_1, v3_elem))
        # End maint _m_Aggr2_out before "Aggr2.remove((v3_1, v3_elem))"
    # Begin maint _m_Aggr2_out after "Aggr2.add((v3_1, v3_val))"
    _maint__m_Aggr2_out_add((v3_1, v3_val))
    # End maint _m_Aggr2_out after "Aggr2.add((v3_1, v3_val))"

def _maint_Aggr1_add(_e):
    v1_val = _m_Aggr1_u.singlelookup((), (0, 0))
    (v1_state, v1_count) = v1_val
    v1_state = (v1_state + 1)
    v1_val = (v1_state, (v1_count + 1))
    if (not (len((_m_Aggr1_u[()] if (() in _m_Aggr1_u) else set())) == 0)):
        v1_elem = _m_Aggr1_u.singlelookup(())
        # Begin maint _m_Aggr1_u before "Aggr1.remove(v1_elem)"
        _maint__m_Aggr1_u_remove(v1_elem)
        # End maint _m_Aggr1_u before "Aggr1.remove(v1_elem)"
    # Begin maint _m_Aggr1_u after "Aggr1.add(v1_val)"
    _maint__m_Aggr1_u_add(v1_val)
    # End maint _m_Aggr1_u after "Aggr1.add(v1_val)"

for (x, y, z) in [(1, 2, 3), (1, 4, 5), (6, 7, 8)]:
    # Begin maint Aggr2 after "R.add((x, y, z))"
    _maint_Aggr2_add((x, y, z))
    # End maint Aggr2 after "R.add((x, y, z))"
    # Begin maint Aggr1 after "R.add((x, y, z))"
    _maint_Aggr1_add((x, y, z))
    # End maint Aggr1 after "R.add((x, y, z))"
a = 1
print(_m_Aggr1_u.singlelookup((), (0, 0))[0])
print(_m_Aggr2_out.singlelookup(a, (0, 0))[0])