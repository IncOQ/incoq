# Q1 : {(a,) for (a, a_2) in REL(S) if (a == a_2)} : {(Number)}
# Q2 : {(v,) for (v,) in REL(R_Q1) if (v > 1)} : {(Bottom)}
from incoq.mars.runtime import *
# R_Q1 : {(Number)}
R_Q1 = CSet()
# R_Q2 : {(Bottom)}
R_Q2 = Set()
def main():
    for (x, y) in [(1, 1), (1, 2), (2, 2), (2, 3)]:
        _v1 = (x, y)
        # Begin inlined _maint_R_Q1_for_S_add.
        (_i3_elem,) = (_v1,)
        # Cost: O(1)
        (_i3_v2_a, _i3_v2_a_2) = _i3_elem
        if (_i3_v2_a == _i3_v2_a_2):
            _i3_v2_result = (_i3_v2_a,)
            if (_i3_v2_result not in R_Q1):
                R_Q1.add(_i3_v2_result)
                # Begin inlined _maint_R_Q2_for_R_Q1_add.
                (_i3_i1_elem,) = (_i3_v2_result,)
                # Cost: O(1)
                (_i3_i1_v4_v,) = _i3_i1_elem
                if (_i3_i1_v4_v > 1):
                    _i3_i1_v4_result = (_i3_i1_v4_v,)
                    R_Q2.add(_i3_i1_v4_result)
                # End inlined _maint_R_Q2_for_R_Q1_add.
            else:
                R_Q1.inccount(_i3_v2_result)
        # End inlined _maint_R_Q1_for_S_add.
    print(sorted(R_Q2))

if (__name__ == '__main__'):
    main()
