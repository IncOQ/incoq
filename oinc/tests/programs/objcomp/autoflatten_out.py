from oinc.runtime import *
# Comp1 := {x : x in R}
Comp1 = RCSet()
def _maint_Comp1_R_add(_e):
    # Iterate {v1_x : v1_x in deltamatch(R, 'b', _e, 1)}
    v1_x = _e
    Comp1.add(v1_x)

def _maint_Comp1_R_remove(_e):
    # Iterate {v2_x : v2_x in deltamatch(R, 'b', _e, 1)}
    v2_x = _e
    Comp1.remove(v2_x)

for i in range(1, 5):
    # Begin maint Comp1 after "R.add(i)"
    _maint_Comp1_R_add(i)
    # End maint Comp1 after "R.add(i)"
print(sorted(Comp1))
# Begin maint Comp1 before "R.remove(3)"
_maint_Comp1_R_remove(3)
# End maint Comp1 before "R.remove(3)"
print(sorted(Comp1))
S = Set()
o = Obj()
o.a = 1