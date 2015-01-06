from oinc.runtime import *
# Comp1 := {(s, t, o_i) : (s, o) in _M, (t, o) in _M, (o, o_i) in _F_i}
_m_Comp1_bbu = Map()
def _maint__m_Comp1_bbu_add(_e):
    (v7_1, v7_2, v7_3) = _e
    if ((v7_1, v7_2) not in _m_Comp1_bbu):
        _m_Comp1_bbu[(v7_1, v7_2)] = set()
    _m_Comp1_bbu[(v7_1, v7_2)].add(v7_3)

def _maint__m_Comp1_bbu_remove(_e):
    (v8_1, v8_2, v8_3) = _e
    _m_Comp1_bbu[(v8_1, v8_2)].remove(v8_3)
    if (len(_m_Comp1_bbu[(v8_1, v8_2)]) == 0):
        del _m_Comp1_bbu[(v8_1, v8_2)]

_m__M_in = Map()
def _maint__m__M_in_add(_e):
    (v5_1, v5_2) = _e
    if (v5_2 not in _m__M_in):
        _m__M_in[v5_2] = set()
    _m__M_in[v5_2].add(v5_1)

Comp1 = RCSet()
def _maint_Comp1__M_add(_e):
    v1_DAS = set()
    # Iterate {(v1_s, v1_o, v1_t, v1_o_i) : (v1_s, v1_o) in deltamatch(_M, 'bb', _e, 1), (v1_t, v1_o) in _M, (v1_o, v1_o_i) in _F_i}
    (v1_s, v1_o) = _e
    if hasattr(v1_o, 'i'):
        v1_o_i = v1_o.i
        for v1_t in (_m__M_in[v1_o] if (v1_o in _m__M_in) else set()):
            if ((v1_s, v1_o, v1_t, v1_o_i) not in v1_DAS):
                v1_DAS.add((v1_s, v1_o, v1_t, v1_o_i))
    # Iterate {(v1_s, v1_o, v1_t, v1_o_i) : (v1_s, v1_o) in _M, (v1_t, v1_o) in deltamatch(_M, 'bb', _e, 1), (v1_o, v1_o_i) in _F_i}
    (v1_t, v1_o) = _e
    if hasattr(v1_o, 'i'):
        v1_o_i = v1_o.i
        for v1_s in (_m__M_in[v1_o] if (v1_o in _m__M_in) else set()):
            if ((v1_s, v1_o, v1_t, v1_o_i) not in v1_DAS):
                v1_DAS.add((v1_s, v1_o, v1_t, v1_o_i))
    for (v1_s, v1_o, v1_t, v1_o_i) in v1_DAS:
        if ((v1_s, v1_t, v1_o_i) not in Comp1):
            Comp1.add((v1_s, v1_t, v1_o_i))
            # Begin maint _m_Comp1_bbu after "Comp1.add((v1_s, v1_t, v1_o_i))"
            _maint__m_Comp1_bbu_add((v1_s, v1_t, v1_o_i))
            # End maint _m_Comp1_bbu after "Comp1.add((v1_s, v1_t, v1_o_i))"
        else:
            Comp1.incref((v1_s, v1_t, v1_o_i))
    del v1_DAS

def _maint_Comp1__F_i_add(_e):
    # Iterate {(v3_s, v3_o, v3_t, v3_o_i) : (v3_s, v3_o) in _M, (v3_t, v3_o) in _M, (v3_o, v3_o_i) in deltamatch(_F_i, 'bb', _e, 1)}
    (v3_o, v3_o_i) = _e
    for v3_s in (_m__M_in[v3_o] if (v3_o in _m__M_in) else set()):
        for v3_t in (_m__M_in[v3_o] if (v3_o in _m__M_in) else set()):
            if ((v3_s, v3_t, v3_o_i) not in Comp1):
                Comp1.add((v3_s, v3_t, v3_o_i))
                # Begin maint _m_Comp1_bbu after "Comp1.add((v3_s, v3_t, v3_o_i))"
                _maint__m_Comp1_bbu_add((v3_s, v3_t, v3_o_i))
                # End maint _m_Comp1_bbu after "Comp1.add((v3_s, v3_t, v3_o_i))"
            else:
                Comp1.incref((v3_s, v3_t, v3_o_i))

s1 = Set()
s2 = Set()
t = Set()
for i in {1, 2, 3, 4, 5}:
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
    t.add(o)
    # Begin maint _m__M_in after "_M.add((t, o))"
    _maint__m__M_in_add((t, o))
    # End maint _m__M_in after "_M.add((t, o))"
    # Begin maint Comp1 after "_M.add((t, o))"
    _maint_Comp1__M_add((t, o))
    # End maint Comp1 after "_M.add((t, o))"
s = s1
print(sorted((_m_Comp1_bbu[(s, t)] if ((s, t) in _m_Comp1_bbu) else set())))
s = s2
print(sorted((_m_Comp1_bbu[(s, t)] if ((s, t) in _m_Comp1_bbu) else set())))