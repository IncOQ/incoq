from invinc.runtime import *
# Comp1 := {(f(x), (y + 1), None) : (x, y) in S}
Comp1 = RCSet()
def _maint_Comp1_S_add(_e):
    # Iterate {(v1_x, v1_y) : (v1_x, v1_y) in deltamatch(S, 'bb', _e, 1)}
    (v1_x, v1_y) = _e
    if ((f(v1_x), (v1_y + 1), None) not in Comp1):
        Comp1.add((f(v1_x), (v1_y + 1), None))
    else:
        Comp1.incref((f(v1_x), (v1_y + 1), None))

def f(y):
    return True

for (v1, v2) in [(1, 2), (3, 4)]:
    # Begin maint Comp1 after "S.add((v1, v2))"
    _maint_Comp1_S_add((v1, v2))
    # End maint Comp1 after "S.add((v1, v2))"
print(sorted(Comp1))