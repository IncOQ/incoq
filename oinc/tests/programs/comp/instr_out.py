from runtimelib import *
# Comp1 := {x : (x, y) in E, f(y)}
Comp1 = RCSet()
def _maint_Comp1_E_add(_e):
    # Iterate {(v1_x, v1_y) : (v1_x, v1_y) in deltamatch(E, 'bb', _e, 1), f(v1_y)}
    (v1_x, v1_y) = _e
    if f(v1_y):
        if (v1_x not in Comp1):
            Comp1.add(v1_x)
        else:
            Comp1.incref(v1_x)

def f(y):
    return True

E = Set()
for (v1, v2) in [(1, 2), (2, 3)]:
    E.add((v1, v2))
    # Begin maint Comp1 after "E.add((v1, v2))"
    _maint_Comp1_E_add((v1, v2))
    # End maint Comp1 after "E.add((v1, v2))"
print(sorted(ENSURE_EQUAL(Comp1, {x for (x, y) in E if f(y)})))