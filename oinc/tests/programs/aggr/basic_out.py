from oinc.runtime import *
# Aggr1 := sum(R, None)
_m_Aggr1_u = Map()
def _maint__m_Aggr1_u_add(_e):
    v3_1 = _e
    if (() not in _m_Aggr1_u):
        _m_Aggr1_u[()] = set()
    _m_Aggr1_u[()].add(v3_1)

def _maint__m_Aggr1_u_remove(_e):
    v4_1 = _e
    _m_Aggr1_u[()].remove(v4_1)
    if (len(_m_Aggr1_u[()]) == 0):
        del _m_Aggr1_u[()]

def _maint_Aggr1_add(_e):
    v1_v1 = _e
    v1_val = _m_Aggr1_u.singlelookup((), (0, 0))
    (v1_state, v1_count) = v1_val
    v1_state = (v1_state + v1_v1)
    v1_val = (v1_state, (v1_count + 1))
    if (not (len((_m_Aggr1_u[()] if (() in _m_Aggr1_u) else set())) == 0)):
        v1_elem = _m_Aggr1_u.singlelookup(())
        # Begin maint _m_Aggr1_u before "Aggr1.remove(v1_elem)"
        _maint__m_Aggr1_u_remove(v1_elem)
        # End maint _m_Aggr1_u before "Aggr1.remove(v1_elem)"
    # Begin maint _m_Aggr1_u after "Aggr1.add(v1_val)"
    _maint__m_Aggr1_u_add(v1_val)
    # End maint _m_Aggr1_u after "Aggr1.add(v1_val)"

def _maint_Aggr1_remove(_e):
    v2_v1 = _e
    v2_val = _m_Aggr1_u.singlelookup(())
    if (v2_val[1] == 1):
        v2_elem = _m_Aggr1_u.singlelookup(())
        # Begin maint _m_Aggr1_u before "Aggr1.remove(v2_elem)"
        _maint__m_Aggr1_u_remove(v2_elem)
        # End maint _m_Aggr1_u before "Aggr1.remove(v2_elem)"
    else:
        (v2_state, v2_count) = v2_val
        v2_state = (v2_state - v2_v1)
        v2_val = (v2_state, (v2_count - 1))
        v2_elem = _m_Aggr1_u.singlelookup(())
        # Begin maint _m_Aggr1_u before "Aggr1.remove(v2_elem)"
        _maint__m_Aggr1_u_remove(v2_elem)
        # End maint _m_Aggr1_u before "Aggr1.remove(v2_elem)"
        # Begin maint _m_Aggr1_u after "Aggr1.add(v2_val)"
        _maint__m_Aggr1_u_add(v2_val)
        # End maint _m_Aggr1_u after "Aggr1.add(v2_val)"

for x in [1, 2, 3, 4, 5]:
    # Begin maint Aggr1 after "R.add(x)"
    _maint_Aggr1_add(x)
    # End maint Aggr1 after "R.add(x)"
# Begin maint Aggr1 before "R.remove(5)"
_maint_Aggr1_remove(5)
# End maint Aggr1 before "R.remove(5)"
print(_m_Aggr1_u.singlelookup((), (0, 0))[0])
for x in [1, 2, 3, 4]:
    # Begin maint Aggr1 before "R.remove(x)"
    _maint_Aggr1_remove(x)
    # End maint Aggr1 before "R.remove(x)"
print(_m_Aggr1_u.singlelookup((), (0, 0))[0])