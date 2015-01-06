from runtimelib import *
# Comp1 := {x : (x, y) in E, f(y)}
# Comp4 := {(x, z) : (x, y) in E, (y, z) in E}
_m_E_in = Map()
def _maint__m_E_in_add(_e):
    (v7_1, v7_2) = _e
    if (v7_2 not in _m_E_in):
        _m_E_in[v7_2] = set()
    _m_E_in[v7_2].add(v7_1)

def _maint__m_E_in_remove(_e):
    (v8_1, v8_2) = _e
    _m_E_in[v8_2].remove(v8_1)
    if (len(_m_E_in[v8_2]) == 0):
        del _m_E_in[v8_2]

_m_E_out = Map()
def _maint__m_E_out_add(_e):
    (v5_1, v5_2) = _e
    if (v5_1 not in _m_E_out):
        _m_E_out[v5_1] = set()
    _m_E_out[v5_1].add(v5_2)

def _maint__m_E_out_remove(_e):
    (v6_1, v6_2) = _e
    _m_E_out[v6_1].remove(v6_2)
    if (len(_m_E_out[v6_1]) == 0):
        del _m_E_out[v6_1]

Comp4 = RCSet()
def _maint_Comp4_E_add(_e):
    v3_DAS = set()
    # Iterate {(v3_x, v3_y, v3_z) : (v3_x, v3_y) in deltamatch(E, 'bb', _e, 1), (v3_y, v3_z) in E}
    (v3_x, v3_y) = _e
    for v3_z in (_m_E_out[v3_y] if (v3_y in _m_E_out) else set()):
        if ((v3_x, v3_y, v3_z) not in v3_DAS):
            v3_DAS.add((v3_x, v3_y, v3_z))
    # Iterate {(v3_x, v3_y, v3_z) : (v3_x, v3_y) in E, (v3_y, v3_z) in deltamatch(E, 'bb', _e, 1)}
    (v3_y, v3_z) = _e
    for v3_x in (_m_E_in[v3_y] if (v3_y in _m_E_in) else set()):
        if ((v3_x, v3_y, v3_z) not in v3_DAS):
            v3_DAS.add((v3_x, v3_y, v3_z))
    for (v3_x, v3_y, v3_z) in v3_DAS:
        if ((v3_x, v3_z) not in Comp4):
            Comp4.add((v3_x, v3_z))
        else:
            Comp4.incref((v3_x, v3_z))
    del v3_DAS

def _maint_Comp4_E_remove(_e):
    v4_DAS = set()
    # Iterate {(v4_x, v4_y, v4_z) : (v4_x, v4_y) in deltamatch(E, 'bb', _e, 1), (v4_y, v4_z) in E}
    (v4_x, v4_y) = _e
    for v4_z in (_m_E_out[v4_y] if (v4_y in _m_E_out) else set()):
        if ((v4_x, v4_y, v4_z) not in v4_DAS):
            v4_DAS.add((v4_x, v4_y, v4_z))
    # Iterate {(v4_x, v4_y, v4_z) : (v4_x, v4_y) in E, (v4_y, v4_z) in deltamatch(E, 'bb', _e, 1)}
    (v4_y, v4_z) = _e
    for v4_x in (_m_E_in[v4_y] if (v4_y in _m_E_in) else set()):
        if ((v4_x, v4_y, v4_z) not in v4_DAS):
            v4_DAS.add((v4_x, v4_y, v4_z))
    for (v4_x, v4_y, v4_z) in v4_DAS:
        if (Comp4.getref((v4_x, v4_z)) == 1):
            Comp4.remove((v4_x, v4_z))
        else:
            Comp4.decref((v4_x, v4_z))
    del v4_DAS

Comp1 = RCSet()
def _maint_Comp1_E_add(_e):
    # Iterate {(v1_x, v1_y) : (v1_x, v1_y) in deltamatch(E, 'bb', _e, 1), f(v1_y)}
    (v1_x, v1_y) = _e
    if f(v1_y):
        if (v1_x not in Comp1):
            Comp1.add(v1_x)
        else:
            Comp1.incref(v1_x)

def _maint_Comp1_E_remove(_e):
    # Iterate {(v2_x, v2_y) : (v2_x, v2_y) in deltamatch(E, 'bb', _e, 1), f(v2_y)}
    (v2_x, v2_y) = _e
    if f(v2_y):
        if (Comp1.getref(v2_x) == 1):
            Comp1.remove(v2_x)
        else:
            Comp1.decref(v2_x)

def f(y):
    return True

E = Set()
R = Set()
T = Set()
V = Set()
for (v1, v2) in [(1, 2), (1, 3), (2, 3), (3, 4)]:
    R.add((v1, v2))
T.add((3, 4))
V.add((5, 5))
def query():
    print(sorted(Comp1))
    print(sorted(Comp4))

for _upelem in R:
    if (_upelem not in E):
        E.add(_upelem)
        # Begin maint _m_E_in after "E.add(_upelem)"
        _maint__m_E_in_add(_upelem)
        # End maint _m_E_in after "E.add(_upelem)"
        # Begin maint _m_E_out after "E.add(_upelem)"
        _maint__m_E_out_add(_upelem)
        # End maint _m_E_out after "E.add(_upelem)"
        # Begin maint Comp4 after "E.add(_upelem)"
        _maint_Comp4_E_add(_upelem)
        # End maint Comp4 after "E.add(_upelem)"
        # Begin maint Comp1 after "E.add(_upelem)"
        _maint_Comp1_E_add(_upelem)
        # End maint Comp1 after "E.add(_upelem)"
query()
for _upelem in list(T):
    if (_upelem in E):
        # Begin maint Comp1 before "E.remove(_upelem)"
        _maint_Comp1_E_remove(_upelem)
        # End maint Comp1 before "E.remove(_upelem)"
        # Begin maint Comp4 before "E.remove(_upelem)"
        _maint_Comp4_E_remove(_upelem)
        # End maint Comp4 before "E.remove(_upelem)"
        # Begin maint _m_E_out before "E.remove(_upelem)"
        _maint__m_E_out_remove(_upelem)
        # End maint _m_E_out before "E.remove(_upelem)"
        # Begin maint _m_E_in before "E.remove(_upelem)"
        _maint__m_E_in_remove(_upelem)
        # End maint _m_E_in before "E.remove(_upelem)"
        E.remove(_upelem)
query()
for _upelem in list(V):
    if (_upelem in E):
        # Begin maint Comp1 before "E.remove(_upelem)"
        _maint_Comp1_E_remove(_upelem)
        # End maint Comp1 before "E.remove(_upelem)"
        # Begin maint Comp4 before "E.remove(_upelem)"
        _maint_Comp4_E_remove(_upelem)
        # End maint Comp4 before "E.remove(_upelem)"
        # Begin maint _m_E_out before "E.remove(_upelem)"
        _maint__m_E_out_remove(_upelem)
        # End maint _m_E_out before "E.remove(_upelem)"
        # Begin maint _m_E_in before "E.remove(_upelem)"
        _maint__m_E_in_remove(_upelem)
        # End maint _m_E_in before "E.remove(_upelem)"
        E.remove(_upelem)
    else:
        E.add(_upelem)
        # Begin maint _m_E_in after "E.add(_upelem)"
        _maint__m_E_in_add(_upelem)
        # End maint _m_E_in after "E.add(_upelem)"
        # Begin maint _m_E_out after "E.add(_upelem)"
        _maint__m_E_out_add(_upelem)
        # End maint _m_E_out after "E.add(_upelem)"
        # Begin maint Comp4 after "E.add(_upelem)"
        _maint_Comp4_E_add(_upelem)
        # End maint Comp4 after "E.add(_upelem)"
        # Begin maint Comp1 after "E.add(_upelem)"
        _maint_Comp1_E_add(_upelem)
        # End maint Comp1 after "E.add(_upelem)"
query()
for _upelem in list(E):
    if (_upelem not in V):
        # Begin maint Comp1 before "E.remove(_upelem)"
        _maint_Comp1_E_remove(_upelem)
        # End maint Comp1 before "E.remove(_upelem)"
        # Begin maint Comp4 before "E.remove(_upelem)"
        _maint_Comp4_E_remove(_upelem)
        # End maint Comp4 before "E.remove(_upelem)"
        # Begin maint _m_E_out before "E.remove(_upelem)"
        _maint__m_E_out_remove(_upelem)
        # End maint _m_E_out before "E.remove(_upelem)"
        # Begin maint _m_E_in before "E.remove(_upelem)"
        _maint__m_E_in_remove(_upelem)
        # End maint _m_E_in before "E.remove(_upelem)"
        E.remove(_upelem)
query()