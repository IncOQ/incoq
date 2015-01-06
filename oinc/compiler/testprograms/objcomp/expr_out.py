from runtimelib import *
# Comp1 := {(s, (o_i + 1)) : (s, o) in _M, (o, o_i) in _F_i}
# Comp6 := {(s, None) : (s, _) in _M}
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

_m__M_in = Map()
def _maint__m__M_in_add(_e):
    (v9_1, v9_2) = _e
    if (v9_2 not in _m__M_in):
        _m__M_in[v9_2] = set()
    _m__M_in[v9_2].add(v9_1)

_m__M_bw = Map()
def _maint__m__M_bw_add(_e):
    (v7_1, v7_2) = _e
    if (v7_1 not in _m__M_bw):
        _m__M_bw[v7_1] = RCSet()
    if (() not in _m__M_bw[v7_1]):
        _m__M_bw[v7_1].add(())
    else:
        _m__M_bw[v7_1].incref(())

Comp6 = RCSet()
def _maint_Comp6__M_add(_e):
    # Iterate {v5_s : (v5_s, _) in deltamatch(_M, 'bw', _e, 1)}
    for v5_s in setmatch(({_e} if ((_m__M_bw[_e[0]] if (_e[0] in _m__M_bw) else RCSet()).getref(()) == 1) else {}), 'uw', ()):
        if ((v5_s, None) not in Comp6):
            Comp6.add((v5_s, None))
            # Begin maint _m_Comp6_out after "Comp6.add((v5_s, None))"
            _maint__m_Comp6_out_add((v5_s, None))
            # End maint _m_Comp6_out after "Comp6.add((v5_s, None))"
        else:
            Comp6.incref((v5_s, None))

Comp1 = RCSet()
def _maint_Comp1__M_add(_e):
    # Iterate {(v1_s, v1_o, v1_o_i) : (v1_s, v1_o) in deltamatch(_M, 'bb', _e, 1), (v1_o, v1_o_i) in _F_i}
    (v1_s, v1_o) = _e
    if hasattr(v1_o, 'i'):
        v1_o_i = v1_o.i
        if ((v1_s, (v1_o_i + 1)) not in Comp1):
            Comp1.add((v1_s, (v1_o_i + 1)))
            # Begin maint _m_Comp1_out after "Comp1.add((v1_s, (v1_o_i + 1)))"
            _maint__m_Comp1_out_add((v1_s, (v1_o_i + 1)))
            # End maint _m_Comp1_out after "Comp1.add((v1_s, (v1_o_i + 1)))"
        else:
            Comp1.incref((v1_s, (v1_o_i + 1)))

def _maint_Comp1__F_i_add(_e):
    # Iterate {(v3_s, v3_o, v3_o_i) : (v3_s, v3_o) in _M, (v3_o, v3_o_i) in deltamatch(_F_i, 'bb', _e, 1)}
    (v3_o, v3_o_i) = _e
    for v3_s in (_m__M_in[v3_o] if (v3_o in _m__M_in) else set()):
        if ((v3_s, (v3_o_i + 1)) not in Comp1):
            Comp1.add((v3_s, (v3_o_i + 1)))
            # Begin maint _m_Comp1_out after "Comp1.add((v3_s, (v3_o_i + 1)))"
            _maint__m_Comp1_out_add((v3_s, (v3_o_i + 1)))
            # End maint _m_Comp1_out after "Comp1.add((v3_s, (v3_o_i + 1)))"
        else:
            Comp1.incref((v3_s, (v3_o_i + 1)))

s = Set()
for i in [1, 2, 3]:
    o = Obj()
    o.i = i
    # Begin maint Comp1 after "_F_i.add((o, i))"
    _maint_Comp1__F_i_add((o, i))
    # End maint Comp1 after "_F_i.add((o, i))"
    s.add(o)
    # Begin maint _m__M_in after "_M.add((s, o))"
    _maint__m__M_in_add((s, o))
    # End maint _m__M_in after "_M.add((s, o))"
    # Begin maint _m__M_bw after "_M.add((s, o))"
    _maint__m__M_bw_add((s, o))
    # End maint _m__M_bw after "_M.add((s, o))"
    # Begin maint Comp6 after "_M.add((s, o))"
    _maint_Comp6__M_add((s, o))
    # End maint Comp6 after "_M.add((s, o))"
    # Begin maint Comp1 after "_M.add((s, o))"
    _maint_Comp1__M_add((s, o))
    # End maint Comp1 after "_M.add((s, o))"
print(sorted((_m_Comp1_out[s] if (s in _m_Comp1_out) else set())))
print((_m_Comp6_out[s] if (s in _m_Comp6_out) else set()))