from oinc.runtime import *
# Aggr1 := min(R, None)
# Aggr2 := max(R, None)
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

_m_Aggr2_u = Map()
def _maint__m_Aggr2_u_add(_e):
    v5_1 = _e
    if (() not in _m_Aggr2_u):
        _m_Aggr2_u[()] = set()
    _m_Aggr2_u[()].add(v5_1)

def _maint__m_Aggr2_u_remove(_e):
    v6_1 = _e
    _m_Aggr2_u[()].remove(v6_1)
    if (len(_m_Aggr2_u[()]) == 0):
        del _m_Aggr2_u[()]

def _maint_Aggr2_add(_e):
    v3_v1 = _e
    v3_val = _m_Aggr2_u.singlelookup((), ((Tree(), None), 0))
    (v3_state, v3_count) = v3_val
    (v3_tree, _) = v3_state
    v3_tree[v3_v1] = None
    v3_state = (v3_tree, v3_tree.__max__())
    v3_val = (v3_state, (v3_count + 1))
    if (not (len((_m_Aggr2_u[()] if (() in _m_Aggr2_u) else set())) == 0)):
        v3_elem = _m_Aggr2_u.singlelookup(())
        # Begin maint _m_Aggr2_u before "Aggr2.remove(v3_elem)"
        _maint__m_Aggr2_u_remove(v3_elem)
        # End maint _m_Aggr2_u before "Aggr2.remove(v3_elem)"
    # Begin maint _m_Aggr2_u after "Aggr2.add(v3_val)"
    _maint__m_Aggr2_u_add(v3_val)
    # End maint _m_Aggr2_u after "Aggr2.add(v3_val)"

def _maint_Aggr2_remove(_e):
    v4_v1 = _e
    v4_val = _m_Aggr2_u.singlelookup(())
    if (v4_val[1] == 1):
        v4_elem = _m_Aggr2_u.singlelookup(())
        # Begin maint _m_Aggr2_u before "Aggr2.remove(v4_elem)"
        _maint__m_Aggr2_u_remove(v4_elem)
        # End maint _m_Aggr2_u before "Aggr2.remove(v4_elem)"
    else:
        (v4_state, v4_count) = v4_val
        (v4_tree, _) = v4_state
        del v4_tree[v4_v1]
        v4_state = (v4_tree, v4_tree.__max__())
        v4_val = (v4_state, (v4_count - 1))
        v4_elem = _m_Aggr2_u.singlelookup(())
        # Begin maint _m_Aggr2_u before "Aggr2.remove(v4_elem)"
        _maint__m_Aggr2_u_remove(v4_elem)
        # End maint _m_Aggr2_u before "Aggr2.remove(v4_elem)"
        # Begin maint _m_Aggr2_u after "Aggr2.add(v4_val)"
        _maint__m_Aggr2_u_add(v4_val)
        # End maint _m_Aggr2_u after "Aggr2.add(v4_val)"

def _maint_Aggr1_add(_e):
    v1_v1 = _e
    v1_val = _m_Aggr1_u.singlelookup((), ((Tree(), None), 0))
    (v1_state, v1_count) = v1_val
    (v1_tree, _) = v1_state
    v1_tree[v1_v1] = None
    v1_state = (v1_tree, v1_tree.__min__())
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
        (v2_tree, _) = v2_state
        del v2_tree[v2_v1]
        v2_state = (v2_tree, v2_tree.__min__())
        v2_val = (v2_state, (v2_count - 1))
        v2_elem = _m_Aggr1_u.singlelookup(())
        # Begin maint _m_Aggr1_u before "Aggr1.remove(v2_elem)"
        _maint__m_Aggr1_u_remove(v2_elem)
        # End maint _m_Aggr1_u before "Aggr1.remove(v2_elem)"
        # Begin maint _m_Aggr1_u after "Aggr1.add(v2_val)"
        _maint__m_Aggr1_u_add(v2_val)
        # End maint _m_Aggr1_u after "Aggr1.add(v2_val)"

for x in [1, 2, 3, 4, 5]:
    # Begin maint Aggr2 after "R.add(x)"
    _maint_Aggr2_add(x)
    # End maint Aggr2 after "R.add(x)"
    # Begin maint Aggr1 after "R.add(x)"
    _maint_Aggr1_add(x)
    # End maint Aggr1 after "R.add(x)"
# Begin maint Aggr1 before "R.remove(5)"
_maint_Aggr1_remove(5)
# End maint Aggr1 before "R.remove(5)"
# Begin maint Aggr2 before "R.remove(5)"
_maint_Aggr2_remove(5)
# End maint Aggr2 before "R.remove(5)"
print(_m_Aggr1_u.singlelookup((), ((Tree(), None), 0))[0][1])
print(_m_Aggr2_u.singlelookup((), ((Tree(), None), 0))[0][1])
for x in [1, 2, 3, 4]:
    # Begin maint Aggr1 before "R.remove(x)"
    _maint_Aggr1_remove(x)
    # End maint Aggr1 before "R.remove(x)"
    # Begin maint Aggr2 before "R.remove(x)"
    _maint_Aggr2_remove(x)
    # End maint Aggr2 before "R.remove(x)"