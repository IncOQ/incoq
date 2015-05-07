from incoq.runtime import *
# Comp1 := {x : (x, _) in E}
_m_E_bw = Map()
def _maint__m_E_bw_add(_e):
    (v3_1, v3_2) = _e
    if (v3_1 not in _m_E_bw):
        _m_E_bw[v3_1] = RCSet()
    if (() not in _m_E_bw[v3_1]):
        _m_E_bw[v3_1].add(())
    else:
        _m_E_bw[v3_1].incref(())

Comp1 = RCSet()
def _maint_Comp1_E_add(_e):
    # Iterate {v1_x : (v1_x, _) in deltamatch(E, 'bw', _e, 1)}
    for v1_x in setmatch(({_e} if ((_m_E_bw[_e[0]] if (_e[0] in _m_E_bw) else RCSet()).getref(()) == 1) else {}), 'uw', ()):
        Comp1.add(v1_x)

for (v1, v2) in [(1, 2), (1, 3), (2, 3), (3, 4)]:
    # Begin maint _m_E_bw after "E.add((v1, v2))"
    _maint__m_E_bw_add((v1, v2))
    # End maint _m_E_bw after "E.add((v1, v2))"
    # Begin maint Comp1 after "E.add((v1, v2))"
    _maint_Comp1_E_add((v1, v2))
    # End maint Comp1 after "E.add((v1, v2))"
print(sorted(Comp1))
print(sorted(Comp1))