from runtimelib import *
# Comp1 := {(s, x) : (s, x) in _M, (x, x_a) in _F_a, (x_a > 1)}
# Comp6 := {(s, y_b) : (s, y) in Comp1, (y, y_b) in _F_b}
_m_Comp6_out = Map()
_m__M_in = Map()
_m_Comp1_in = Map()
Comp6 = RCSet()
Comp1 = RCSet()
s = Set()
for i in [1, 2, 3]:
    o = Obj()
    o.a = i
    # Begin maint Comp1 after "_F_a.add((o, i))"
    # End maint Comp1 after "_F_a.add((o, i))"
    o.b = (i * 2)
    # Begin maint Comp6 after "_F_b.add((o, (i * 2)))"
    # End maint Comp6 after "_F_b.add((o, (i * 2)))"
    s.add(o)
    # Begin maint _m__M_in after "_M.add((s, o))"
    # End maint _m__M_in after "_M.add((s, o))"
    # Begin maint Comp1 after "_M.add((s, o))"
    # End maint Comp1 after "_M.add((s, o))"
print(sorted((_m_Comp6_out[s] if (s in _m_Comp6_out) else set())))