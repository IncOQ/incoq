# Check handling of deltas to enumerators with wildcards.

from invinc.runtime import *

QUERYOPTIONS(
    '{(x, w) for (x, x2, z) in S for (x3, w) in T if x == x2 if x2 == x3}',
    impl = 'inc',
)

S = Set()
T = Set()

for v1, v2 in [(1, 3)]:
    T.add((v1, v2))

for v1, v2, v3 in [(1, 2, 2), (1, 1, 2)]:
    S.add((v1, v2, v3))

print(sorted({(x, w) for (x, x2, z) in S for (x3, w) in T if x == x2 if x2 == x3}))

T.remove((1, 3))

print(sorted({(x, w) for (x, x2, z) in S for (x3, w) in T if x == x2 if x2 == x3}))
