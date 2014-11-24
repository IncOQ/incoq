from runtimelib import *
# Comp1 := {(m, k, o_i) : (m, k, m_m_k_k) in _MAP, (m_m_k_k, o) in _M, (o, o_i) in _F_i}
_m_Comp1_bbu = Map()
def _maint__m_Comp1_bbu_add(_e):
    (v11_1, v11_2, v11_3) = _e
    if ((v11_1, v11_2) not in _m_Comp1_bbu):
        _m_Comp1_bbu[(v11_1, v11_2)] = set()
    _m_Comp1_bbu[(v11_1, v11_2)].add(v11_3)

def _maint__m_Comp1_bbu_remove(_e):
    (v12_1, v12_2, v12_3) = _e
    _m_Comp1_bbu[(v12_1, v12_2)].remove(v12_3)
    if (len(_m_Comp1_bbu[(v12_1, v12_2)]) == 0):
        del _m_Comp1_bbu[(v12_1, v12_2)]

_m__M_in = Map()
def _maint__m__M_in_add(_e):
    (v9_1, v9_2) = _e
    if (v9_2 not in _m__M_in):
        _m__M_in[v9_2] = set()
    _m__M_in[v9_2].add(v9_1)

_m__MAP_uub = Map()
def _maint__m__MAP_uub_add(_e):
    (v7_1, v7_2, v7_3) = _e
    if (v7_3 not in _m__MAP_uub):
        _m__MAP_uub[v7_3] = set()
    _m__MAP_uub[v7_3].add((v7_1, v7_2))

Comp1 = RCSet()
def _maint_Comp1__MAP_add(_e):
    # Iterate {(v1_m, v1_k, v1_m_m_k_k, v1_o, v1_o_i) : (v1_m, v1_k, v1_m_m_k_k) in deltamatch(_MAP, 'bbb', _e, 1), (v1_m_m_k_k, v1_o) in _M, (v1_o, v1_o_i) in _F_i}
    (v1_m, v1_k, v1_m_m_k_k) = _e
    if isinstance(v1_m_m_k_k, Set):
        for v1_o in v1_m_m_k_k:
            if hasattr(v1_o, 'i'):
                v1_o_i = v1_o.i
                if ((v1_m, v1_k, v1_o_i) not in Comp1):
                    Comp1.add((v1_m, v1_k, v1_o_i))
                    # Begin maint _m_Comp1_bbu after "Comp1.add((v1_m, v1_k, v1_o_i))"
                    _maint__m_Comp1_bbu_add((v1_m, v1_k, v1_o_i))
                    # End maint _m_Comp1_bbu after "Comp1.add((v1_m, v1_k, v1_o_i))"
                else:
                    Comp1.incref((v1_m, v1_k, v1_o_i))

def _maint_Comp1__M_add(_e):
    # Iterate {(v3_m, v3_k, v3_m_m_k_k, v3_o, v3_o_i) : (v3_m, v3_k, v3_m_m_k_k) in _MAP, (v3_m_m_k_k, v3_o) in deltamatch(_M, 'bb', _e, 1), (v3_o, v3_o_i) in _F_i}
    (v3_m_m_k_k, v3_o) = _e
    if hasattr(v3_o, 'i'):
        v3_o_i = v3_o.i
        for (v3_m, v3_k) in (_m__MAP_uub[v3_m_m_k_k] if (v3_m_m_k_k in _m__MAP_uub) else set()):
            if ((v3_m, v3_k, v3_o_i) not in Comp1):
                Comp1.add((v3_m, v3_k, v3_o_i))
                # Begin maint _m_Comp1_bbu after "Comp1.add((v3_m, v3_k, v3_o_i))"
                _maint__m_Comp1_bbu_add((v3_m, v3_k, v3_o_i))
                # End maint _m_Comp1_bbu after "Comp1.add((v3_m, v3_k, v3_o_i))"
            else:
                Comp1.incref((v3_m, v3_k, v3_o_i))

def _maint_Comp1__F_i_add(_e):
    # Iterate {(v5_m, v5_k, v5_m_m_k_k, v5_o, v5_o_i) : (v5_m, v5_k, v5_m_m_k_k) in _MAP, (v5_m_m_k_k, v5_o) in _M, (v5_o, v5_o_i) in deltamatch(_F_i, 'bb', _e, 1)}
    (v5_o, v5_o_i) = _e
    for v5_m_m_k_k in (_m__M_in[v5_o] if (v5_o in _m__M_in) else set()):
        for (v5_m, v5_k) in (_m__MAP_uub[v5_m_m_k_k] if (v5_m_m_k_k in _m__MAP_uub) else set()):
            if ((v5_m, v5_k, v5_o_i) not in Comp1):
                Comp1.add((v5_m, v5_k, v5_o_i))
                # Begin maint _m_Comp1_bbu after "Comp1.add((v5_m, v5_k, v5_o_i))"
                _maint__m_Comp1_bbu_add((v5_m, v5_k, v5_o_i))
                # End maint _m_Comp1_bbu after "Comp1.add((v5_m, v5_k, v5_o_i))"
            else:
                Comp1.incref((v5_m, v5_k, v5_o_i))

m = Map()
s1 = Set()
s2 = Set()
m['a'] = s1
# Begin maint _m__MAP_uub after "_MAP.add((m, 'a', s1))"
_maint__m__MAP_uub_add((m, 'a', s1))
# End maint _m__MAP_uub after "_MAP.add((m, 'a', s1))"
# Begin maint Comp1 after "_MAP.add((m, 'a', s1))"
_maint_Comp1__MAP_add((m, 'a', s1))
# End maint Comp1 after "_MAP.add((m, 'a', s1))"
m['b'] = s2
# Begin maint _m__MAP_uub after "_MAP.add((m, 'b', s2))"
_maint__m__MAP_uub_add((m, 'b', s2))
# End maint _m__MAP_uub after "_MAP.add((m, 'b', s2))"
# Begin maint Comp1 after "_MAP.add((m, 'b', s2))"
_maint_Comp1__MAP_add((m, 'b', s2))
# End maint Comp1 after "_MAP.add((m, 'b', s2))"
for i in range(10):
    o = Obj()
    o.i = i
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
k = 'a'
print(sorted((_m_Comp1_bbu[(m, k)] if ((m, k) in _m_Comp1_bbu) else set())))
k = 'b'
print(sorted((_m_Comp1_bbu[(m, k)] if ((m, k) in _m_Comp1_bbu) else set())))