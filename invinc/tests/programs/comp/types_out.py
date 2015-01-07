from invinc.runtime import *
# Comp1 := {x.a : x in S}
Comp1 = RCSet()
def _maint_Comp1_S_add(_e):
    # Iterate {v2_x : v2_x in deltamatch(S, 'b', _e, 1)}
    v2_x = _e
    if (v2_x.a not in Comp1):
        Comp1.add(v2_x.a)
    else:
        Comp1.incref(v2_x.a)

class T(Set):
    def __init__(self, v):
        self.a = v
        self.b = 0


v1 = Set()
S = v1
for elem in {T(1), T(2), T(3)}:
    S.add(elem)
    # Begin maint Comp1 after "S.add(elem)"
    _maint_Comp1_S_add(elem)
    # End maint Comp1 after "S.add(elem)"
print(sorted(Comp1))
print(sorted({x.b for x in S}))