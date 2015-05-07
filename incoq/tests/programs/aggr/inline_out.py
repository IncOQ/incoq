from incoq.runtime import *
# Aggr1 := sum(R, None)
_m_Aggr1_u = Map()
for x in [1, 2, 3, 4, 5]:
    # Begin maint Aggr1 after "R.add(x)"
    v1_v1 = x
    v1_val = _m_Aggr1_u.singlelookup((), (0, 0))
    (v1_state, v1_count) = v1_val
    v1_state = (v1_state + v1_v1)
    v1_val = (v1_state, (v1_count + 1))
    if (not (len((_m_Aggr1_u[()] if (() in _m_Aggr1_u) else set())) == 0)):
        v1_elem = _m_Aggr1_u.singlelookup(())
        # Begin maint _m_Aggr1_u before "Aggr1.remove(v1_elem)"
        v4_1 = v1_elem
        _m_Aggr1_u[()].remove(v4_1)
        if (len(_m_Aggr1_u[()]) == 0):
            del _m_Aggr1_u[()]
        # End maint _m_Aggr1_u before "Aggr1.remove(v1_elem)"
    # Begin maint _m_Aggr1_u after "Aggr1.add(v1_val)"
    v3_1 = v1_val
    if (() not in _m_Aggr1_u):
        _m_Aggr1_u[()] = set()
    _m_Aggr1_u[()].add(v3_1)
    # End maint _m_Aggr1_u after "Aggr1.add(v1_val)"
    # End maint Aggr1 after "R.add(x)"
# Begin maint Aggr1 before "R.remove(5)"
v2_v1 = 5
v2_val = _m_Aggr1_u.singlelookup(())
if (v2_val[1] == 1):
    v2_elem = _m_Aggr1_u.singlelookup(())
    # Begin maint _m_Aggr1_u before "Aggr1.remove(v2_elem)"
    v4_1 = v2_elem
    _m_Aggr1_u[()].remove(v4_1)
    if (len(_m_Aggr1_u[()]) == 0):
        del _m_Aggr1_u[()]
    # End maint _m_Aggr1_u before "Aggr1.remove(v2_elem)"
else:
    (v2_state, v2_count) = v2_val
    v2_state = (v2_state - v2_v1)
    v2_val = (v2_state, (v2_count - 1))
    v2_elem = _m_Aggr1_u.singlelookup(())
    # Begin maint _m_Aggr1_u before "Aggr1.remove(v2_elem)"
    v4_1 = v2_elem
    _m_Aggr1_u[()].remove(v4_1)
    if (len(_m_Aggr1_u[()]) == 0):
        del _m_Aggr1_u[()]
    # End maint _m_Aggr1_u before "Aggr1.remove(v2_elem)"
    # Begin maint _m_Aggr1_u after "Aggr1.add(v2_val)"
    v3_1 = v2_val
    if (() not in _m_Aggr1_u):
        _m_Aggr1_u[()] = set()
    _m_Aggr1_u[()].add(v3_1)
    # End maint _m_Aggr1_u after "Aggr1.add(v2_val)"
# End maint Aggr1 before "R.remove(5)"
print(_m_Aggr1_u.singlelookup((), (0, 0))[0])
for x in [1, 2, 3, 4]:
    # Begin maint Aggr1 before "R.remove(x)"
    v2_v1 = x
    v2_val = _m_Aggr1_u.singlelookup(())
    if (v2_val[1] == 1):
        v2_elem = _m_Aggr1_u.singlelookup(())
        # Begin maint _m_Aggr1_u before "Aggr1.remove(v2_elem)"
        v4_1 = v2_elem
        _m_Aggr1_u[()].remove(v4_1)
        if (len(_m_Aggr1_u[()]) == 0):
            del _m_Aggr1_u[()]
        # End maint _m_Aggr1_u before "Aggr1.remove(v2_elem)"
    else:
        (v2_state, v2_count) = v2_val
        v2_state = (v2_state - v2_v1)
        v2_val = (v2_state, (v2_count - 1))
        v2_elem = _m_Aggr1_u.singlelookup(())
        # Begin maint _m_Aggr1_u before "Aggr1.remove(v2_elem)"
        v4_1 = v2_elem
        _m_Aggr1_u[()].remove(v4_1)
        if (len(_m_Aggr1_u[()]) == 0):
            del _m_Aggr1_u[()]
        # End maint _m_Aggr1_u before "Aggr1.remove(v2_elem)"
        # Begin maint _m_Aggr1_u after "Aggr1.add(v2_val)"
        v3_1 = v2_val
        if (() not in _m_Aggr1_u):
            _m_Aggr1_u[()] = set()
        _m_Aggr1_u[()].add(v3_1)
        # End maint _m_Aggr1_u after "Aggr1.add(v2_val)"
    # End maint Aggr1 before "R.remove(x)"
print(_m_Aggr1_u.singlelookup((), (0, 0))[0])