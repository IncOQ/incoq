from oinc.runtime import *
# Comp1 := {(s, x) : (s, x) in _M, (x, x_a) in _F_a, (x_a > 1)}
# Comp6 := {(s, y_b) : (s, y) in Comp1, (y, y_b) in _F_b}
_m_Comp6_out = Map()
def _maint__m_Comp6_out_add(_e):
    (v13_1, v13_2) = _e
    if (v13_1 not in _m_Comp6_out):
        _m_Comp6_out[v13_1] = set()
    _m_Comp6_out[v13_1].add(v13_2)

def _maint__m_Comp6_out_remove(_e):
    (v14_1, v14_2) = _e
    _m_Comp6_out[v14_1].remove(v14_2)
    if (len(_m_Comp6_out[v14_1]) == 0):
        del _m_Comp6_out[v14_1]

_m__M_in = Map()
def _maint__m__M_in_add(_e):
    (v11_1, v11_2) = _e
    if (v11_2 not in _m__M_in):
        _m__M_in[v11_2] = set()
    _m__M_in[v11_2].add(v11_1)

_m_Comp1_in = Map()
def _maint__m_Comp1_in_add(_e):
    (v9_1, v9_2) = _e
    if (v9_2 not in _m_Comp1_in):
        _m_Comp1_in[v9_2] = set()
    _m_Comp1_in[v9_2].add(v9_1)

def _maint__m_Comp1_in_remove(_e):
    (v10_1, v10_2) = _e
    _m_Comp1_in[v10_2].remove(v10_1)
    if (len(_m_Comp1_in[v10_2]) == 0):
        del _m_Comp1_in[v10_2]

Comp6 = RCSet()
def _maint_Comp6_Comp1_add(_e):
    # Iterate {(v5_s, v5_y, v5_y_b) : (v5_s, v5_y) in deltamatch(Comp1, 'bb', _e, 1), (v5_y, v5_y_b) in _F_b}
    (v5_s, v5_y) = _e
    if hasattr(v5_y, 'b'):
        v5_y_b = v5_y.b
        if ((v5_s, v5_y_b) not in Comp6):
            Comp6.add((v5_s, v5_y_b))
            # Begin maint _m_Comp6_out after "Comp6.add((v5_s, v5_y_b))"
            _maint__m_Comp6_out_add((v5_s, v5_y_b))
            # End maint _m_Comp6_out after "Comp6.add((v5_s, v5_y_b))"
        else:
            Comp6.incref((v5_s, v5_y_b))

def _maint_Comp6_Comp1_remove(_e):
    # Iterate {(v6_s, v6_y, v6_y_b) : (v6_s, v6_y) in deltamatch(Comp1, 'bb', _e, 1), (v6_y, v6_y_b) in _F_b}
    (v6_s, v6_y) = _e
    if hasattr(v6_y, 'b'):
        v6_y_b = v6_y.b
        if (Comp6.getref((v6_s, v6_y_b)) == 1):
            # Begin maint _m_Comp6_out before "Comp6.remove((v6_s, v6_y_b))"
            _maint__m_Comp6_out_remove((v6_s, v6_y_b))
            # End maint _m_Comp6_out before "Comp6.remove((v6_s, v6_y_b))"
            Comp6.remove((v6_s, v6_y_b))
        else:
            Comp6.decref((v6_s, v6_y_b))

def _maint_Comp6__F_b_add(_e):
    # Iterate {(v7_s, v7_y, v7_y_b) : (v7_s, v7_y) in Comp1, (v7_y, v7_y_b) in deltamatch(_F_b, 'bb', _e, 1)}
    (v7_y, v7_y_b) = _e
    for v7_s in (_m_Comp1_in[v7_y] if (v7_y in _m_Comp1_in) else set()):
        if ((v7_s, v7_y_b) not in Comp6):
            Comp6.add((v7_s, v7_y_b))
            # Begin maint _m_Comp6_out after "Comp6.add((v7_s, v7_y_b))"
            _maint__m_Comp6_out_add((v7_s, v7_y_b))
            # End maint _m_Comp6_out after "Comp6.add((v7_s, v7_y_b))"
        else:
            Comp6.incref((v7_s, v7_y_b))

Comp1 = RCSet()
def _maint_Comp1__M_add(_e):
    # Iterate {(v1_s, v1_x, v1_x_a) : (v1_s, v1_x) in deltamatch(_M, 'bb', _e, 1), (v1_x, v1_x_a) in _F_a, (v1_x_a > 1)}
    (v1_s, v1_x) = _e
    if hasattr(v1_x, 'a'):
        v1_x_a = v1_x.a
        if (v1_x_a > 1):
            if ((v1_s, v1_x) not in Comp1):
                Comp1.add((v1_s, v1_x))
                # Begin maint _m_Comp1_in after "Comp1.add((v1_s, v1_x))"
                _maint__m_Comp1_in_add((v1_s, v1_x))
                # End maint _m_Comp1_in after "Comp1.add((v1_s, v1_x))"
                # Begin maint Comp6 after "Comp1.add((v1_s, v1_x))"
                _maint_Comp6_Comp1_add((v1_s, v1_x))
                # End maint Comp6 after "Comp1.add((v1_s, v1_x))"
            else:
                Comp1.incref((v1_s, v1_x))

def _maint_Comp1__F_a_add(_e):
    # Iterate {(v3_s, v3_x, v3_x_a) : (v3_s, v3_x) in _M, (v3_x, v3_x_a) in deltamatch(_F_a, 'bb', _e, 1), (v3_x_a > 1)}
    (v3_x, v3_x_a) = _e
    if (v3_x_a > 1):
        for v3_s in (_m__M_in[v3_x] if (v3_x in _m__M_in) else set()):
            if ((v3_s, v3_x) not in Comp1):
                Comp1.add((v3_s, v3_x))
                # Begin maint _m_Comp1_in after "Comp1.add((v3_s, v3_x))"
                _maint__m_Comp1_in_add((v3_s, v3_x))
                # End maint _m_Comp1_in after "Comp1.add((v3_s, v3_x))"
                # Begin maint Comp6 after "Comp1.add((v3_s, v3_x))"
                _maint_Comp6_Comp1_add((v3_s, v3_x))
                # End maint Comp6 after "Comp1.add((v3_s, v3_x))"
            else:
                Comp1.incref((v3_s, v3_x))

s = Set()
for i in [1, 2, 3]:
    o = Obj()
    o.a = i
    # Begin maint Comp1 after "_F_a.add((o, i))"
    _maint_Comp1__F_a_add((o, i))
    # End maint Comp1 after "_F_a.add((o, i))"
    o.b = (i * 2)
    # Begin maint Comp6 after "_F_b.add((o, (i * 2)))"
    _maint_Comp6__F_b_add((o, (i * 2)))
    # End maint Comp6 after "_F_b.add((o, (i * 2)))"
    s.add(o)
    # Begin maint _m__M_in after "_M.add((s, o))"
    _maint__m__M_in_add((s, o))
    # End maint _m__M_in after "_M.add((s, o))"
    # Begin maint Comp1 after "_M.add((s, o))"
    _maint_Comp1__M_add((s, o))
    # End maint Comp1 after "_M.add((s, o))"
print(sorted((_m_Comp6_out[s] if (s in _m_Comp6_out) else set())))