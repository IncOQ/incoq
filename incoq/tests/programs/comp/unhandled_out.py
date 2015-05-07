from incoq.runtime import *
# Comp1 := {(x, y) : x in N, y in N}
Comp1 = RCSet()
def _maint_Comp1_N_add(_e):
    v1_DAS = set()
    # Iterate {(v1_x, v1_y) : v1_x in deltamatch(N, 'b', _e, 1), v1_y in N}
    v1_x = _e
    for v1_y in N:
        if ((v1_x, v1_y) not in v1_DAS):
            v1_DAS.add((v1_x, v1_y))
    # Iterate {(v1_x, v1_y) : v1_x in N, v1_y in deltamatch(N, 'b', _e, 1)}
    v1_y = _e
    for v1_x in N:
        if ((v1_x, v1_y) not in v1_DAS):
            v1_DAS.add((v1_x, v1_y))
    for (v1_x, v1_y) in v1_DAS:
        Comp1.add((v1_x, v1_y))
    del v1_DAS

N = Set()
for i in range(3):
    N.add(i)
    # Begin maint Comp1 after "N.add(i)"
    _maint_Comp1_N_add(i)
    # End maint Comp1 after "N.add(i)"
print(sorted(Comp1))
print(sorted({(x, y) for x in range(3) for y in range(3)}))