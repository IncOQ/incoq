from incoq.runtime import *
# Comp1 := {(x, z) : (x, y) in E, (y, z) in E}
# Aggr1 := sum(setmatch(Comp1, 'bu', x), None)
_m_E_in = Map()
def _maint__m_E_in_add(_e):
    (v9_1, v9_2) = _e
    if (v9_2 not in _m_E_in):
        _m_E_in[v9_2] = set()
    _m_E_in[v9_2].add(v9_1)

_m_E_out = Map()
def _maint__m_E_out_add(_e):
    (v7_1, v7_2) = _e
    if (v7_1 not in _m_E_out):
        _m_E_out[v7_1] = set()
    _m_E_out[v7_1].add(v7_2)

_m_Aggr1_out = Map()
def _maint__m_Aggr1_out_add(_e):
    (v5_1, v5_2) = _e
    if (v5_1 not in _m_Aggr1_out):
        _m_Aggr1_out[v5_1] = set()
    _m_Aggr1_out[v5_1].add(v5_2)

def _maint__m_Aggr1_out_remove(_e):
    (v6_1, v6_2) = _e
    _m_Aggr1_out[v6_1].remove(v6_2)
    if (len(_m_Aggr1_out[v6_1]) == 0):
        del _m_Aggr1_out[v6_1]

def _maint_Aggr1_add(_e):
    (v3_v1, v3_v2) = _e
    v3_val = _m_Aggr1_out.singlelookup(v3_v1, (0, 0))
    (v3_state, v3_count) = v3_val
    v3_state = (v3_state + v3_v2)
    v3_val = (v3_state, (v3_count + 1))
    v3_1 = v3_v1
    if (not (len((_m_Aggr1_out[v3_v1] if (v3_v1 in _m_Aggr1_out) else set())) == 0)):
        v3_elem = _m_Aggr1_out.singlelookup(v3_v1)
        # Begin maint _m_Aggr1_out before "Aggr1.remove((v3_1, v3_elem))"
        _maint__m_Aggr1_out_remove((v3_1, v3_elem))
        # End maint _m_Aggr1_out before "Aggr1.remove((v3_1, v3_elem))"
    # Begin maint _m_Aggr1_out after "Aggr1.add((v3_1, v3_val))"
    _maint__m_Aggr1_out_add((v3_1, v3_val))
    # End maint _m_Aggr1_out after "Aggr1.add((v3_1, v3_val))"

def _maint_Aggr1_remove(_e):
    (v4_v1, v4_v2) = _e
    v4_val = _m_Aggr1_out.singlelookup(v4_v1)
    if (v4_val[1] == 1):
        v4_1 = v4_v1
        v4_elem = _m_Aggr1_out.singlelookup(v4_v1)
        # Begin maint _m_Aggr1_out before "Aggr1.remove((v4_1, v4_elem))"
        _maint__m_Aggr1_out_remove((v4_1, v4_elem))
        # End maint _m_Aggr1_out before "Aggr1.remove((v4_1, v4_elem))"
    else:
        (v4_state, v4_count) = v4_val
        v4_state = (v4_state - v4_v2)
        v4_val = (v4_state, (v4_count - 1))
        v4_1 = v4_v1
        v4_elem = _m_Aggr1_out.singlelookup(v4_v1)
        # Begin maint _m_Aggr1_out before "Aggr1.remove((v4_1, v4_elem))"
        _maint__m_Aggr1_out_remove((v4_1, v4_elem))
        # End maint _m_Aggr1_out before "Aggr1.remove((v4_1, v4_elem))"
        # Begin maint _m_Aggr1_out after "Aggr1.add((v4_1, v4_val))"
        _maint__m_Aggr1_out_add((v4_1, v4_val))
        # End maint _m_Aggr1_out after "Aggr1.add((v4_1, v4_val))"

Comp1 = RCSet()
def _maint_Comp1_E_add(_e):
    v1_DAS = set()
    # Iterate {(v1_x, v1_y, v1_z) : (v1_x, v1_y) in deltamatch(E, 'bb', _e, 1), (v1_y, v1_z) in E}
    (v1_x, v1_y) = _e
    for v1_z in (_m_E_out[v1_y] if (v1_y in _m_E_out) else set()):
        if ((v1_x, v1_y, v1_z) not in v1_DAS):
            v1_DAS.add((v1_x, v1_y, v1_z))
    # Iterate {(v1_x, v1_y, v1_z) : (v1_x, v1_y) in E, (v1_y, v1_z) in deltamatch(E, 'bb', _e, 1)}
    (v1_y, v1_z) = _e
    for v1_x in (_m_E_in[v1_y] if (v1_y in _m_E_in) else set()):
        if ((v1_x, v1_y, v1_z) not in v1_DAS):
            v1_DAS.add((v1_x, v1_y, v1_z))
    for (v1_x, v1_y, v1_z) in v1_DAS:
        if ((v1_x, v1_z) not in Comp1):
            Comp1.add((v1_x, v1_z))
            # Begin maint Aggr1 after "Comp1.add((v1_x, v1_z))"
            _maint_Aggr1_add((v1_x, v1_z))
            # End maint Aggr1 after "Comp1.add((v1_x, v1_z))"
        else:
            Comp1.incref((v1_x, v1_z))
    del v1_DAS

for e in [(1, 2), (2, 3), (2, 4), (3, 5)]:
    # Begin maint _m_E_in after "E.add(e)"
    _maint__m_E_in_add(e)
    # End maint _m_E_in after "E.add(e)"
    # Begin maint _m_E_out after "E.add(e)"
    _maint__m_E_out_add(e)
    # End maint _m_E_out after "E.add(e)"
    # Begin maint Comp1 after "E.add(e)"
    _maint_Comp1_E_add(e)
    # End maint Comp1 after "E.add(e)"
x = 1
print(_m_Aggr1_out.singlelookup(x, (0, 0))[0])