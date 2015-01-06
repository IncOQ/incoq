from runtimelib import *
# Comp1 := {(s, o_i) : (s, o) in _M, (o, o_i) in _F_i, o_i in N}
_m_Comp1_out = Map()
def _maint__m_Comp1_out_add(_e):
    (v11_1, v11_2) = _e
    if (v11_1 not in _m_Comp1_out):
        _m_Comp1_out[v11_1] = set()
    _m_Comp1_out[v11_1].add(v11_2)

def _maint__m_Comp1_out_remove(_e):
    (v12_1, v12_2) = _e
    _m_Comp1_out[v12_1].remove(v12_2)
    if (len(_m_Comp1_out[v12_1]) == 0):
        del _m_Comp1_out[v12_1]

_m__F_i_in = Map()
def _maint__m__F_i_in_add(_e):
    (v9_1, v9_2) = _e
    if (v9_2 not in _m__F_i_in):
        _m__F_i_in[v9_2] = set()
    _m__F_i_in[v9_2].add(v9_1)

_m__M_in = Map()
def _maint__m__M_in_add(_e):
    (v7_1, v7_2) = _e
    if (v7_2 not in _m__M_in):
        _m__M_in[v7_2] = set()
    _m__M_in[v7_2].add(v7_1)

Comp1 = RCSet()
def _maint_Comp1__M_add(_e):
    # Iterate {(v1_s, v1_o, v1_o_i) : (v1_s, v1_o) in deltamatch(_M, 'bb', _e, 1), (v1_o, v1_o_i) in _F_i, v1_o_i in N}
    (v1_s, v1_o) = _e
    if hasattr(v1_o, 'i'):
        v1_o_i = v1_o.i
        if (v1_o_i in N):
            if ((v1_s, v1_o_i) not in Comp1):
                Comp1.add((v1_s, v1_o_i))
                # Begin maint _m_Comp1_out after "Comp1.add((v1_s, v1_o_i))"
                _maint__m_Comp1_out_add((v1_s, v1_o_i))
                # End maint _m_Comp1_out after "Comp1.add((v1_s, v1_o_i))"
            else:
                Comp1.incref((v1_s, v1_o_i))

def _maint_Comp1__F_i_add(_e):
    # Iterate {(v3_s, v3_o, v3_o_i) : (v3_s, v3_o) in _M, (v3_o, v3_o_i) in deltamatch(_F_i, 'bb', _e, 1), v3_o_i in N}
    (v3_o, v3_o_i) = _e
    if (v3_o_i in N):
        for v3_s in (_m__M_in[v3_o] if (v3_o in _m__M_in) else set()):
            if ((v3_s, v3_o_i) not in Comp1):
                Comp1.add((v3_s, v3_o_i))
                # Begin maint _m_Comp1_out after "Comp1.add((v3_s, v3_o_i))"
                _maint__m_Comp1_out_add((v3_s, v3_o_i))
                # End maint _m_Comp1_out after "Comp1.add((v3_s, v3_o_i))"
            else:
                Comp1.incref((v3_s, v3_o_i))

def _maint_Comp1_N_add(_e):
    # Iterate {(v5_s, v5_o, v5_o_i) : (v5_s, v5_o) in _M, (v5_o, v5_o_i) in _F_i, v5_o_i in deltamatch(N, 'b', _e, 1)}
    v5_o_i = _e
    for v5_o in (_m__F_i_in[v5_o_i] if (v5_o_i in _m__F_i_in) else set()):
        for v5_s in (_m__M_in[v5_o] if (v5_o in _m__M_in) else set()):
            if ((v5_s, v5_o_i) not in Comp1):
                Comp1.add((v5_s, v5_o_i))
                # Begin maint _m_Comp1_out after "Comp1.add((v5_s, v5_o_i))"
                _maint__m_Comp1_out_add((v5_s, v5_o_i))
                # End maint _m_Comp1_out after "Comp1.add((v5_s, v5_o_i))"
            else:
                Comp1.incref((v5_s, v5_o_i))

N = Set()
for i in range(1, 5):
    N.add(i)
    # Begin maint Comp1 after "N.add(i)"
    _maint_Comp1_N_add(i)
    # End maint Comp1 after "N.add(i)"
s1 = Set()
s2 = Set()
for i in N:
    o = Obj()
    o.i = i
    # Begin maint _m__F_i_in after "_F_i.add((o, i))"
    _maint__m__F_i_in_add((o, i))
    # End maint _m__F_i_in after "_F_i.add((o, i))"
    # Begin maint Comp1 after "_F_i.add((o, i))"
    _maint_Comp1__F_i_add((o, i))
    # End maint Comp1 after "_F_i.add((o, i))"
    if (i % 2):
        s1.add(o)
        # Begin maint _m__M_in after "_M.add((s1, o))"
        _maint__m__M_in_add((s1, o))
        # End maint _m__M_in after "_M.add((s1, o))"
        # Begin maint Comp1 after "_M.add((s1, o))"
        _maint_Comp1__M_add((s1, o))
        # End maint Comp1 after "_M.add((s1, o))"
    else:
        s2.add(o)
        # Begin maint _m__M_in after "_M.add((s2, o))"
        _maint__m__M_in_add((s2, o))
        # End maint _m__M_in after "_M.add((s2, o))"
        # Begin maint Comp1 after "_M.add((s2, o))"
        _maint_Comp1__M_add((s2, o))
        # End maint Comp1 after "_M.add((s2, o))"
s = s1
print(sorted((_m_Comp1_out[s] if (s in _m_Comp1_out) else set())))
s = s2
print(sorted((_m_Comp1_out[s] if (s in _m_Comp1_out) else set())))