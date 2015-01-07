# Check handling of deltas to enumerators with equalities.

from invinc.runtime import *

QUERYOPTIONS(
    '{(x, w) for (x, x2, z) in S for (z2, w) in T if x == x2 if z == z2}',
    impl = 'inc',
)

S = Set()
T = Set()

for v1, v2 in [(2, 4), (3, 5)]:
    T.add((v1, v2))

for v1, v2, v3 in [(1, 1, 2), (1, 2, 3)]:
    S.add((v1, v2, v3))

print(sorted({(x, w) for (x, x2, z) in S for (z2, w) in T if x == x2 if z == z2}))
