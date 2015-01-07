# Auxmaps with equality constraints.

from invinc.runtime import *

P = Set()

for v in [(1, 1, 2), (1, 2, 2), (3, 4, 2), (5, 6, 7)]:
    P.add(v)

print(sorted(setmatch(P, 'uwb', 2)))

P.remove((1, 1, 2))

print(sorted(setmatch(P, 'uwb', 2)))

P.remove((1, 2, 2))

print(sorted(setmatch(P, 'uwb', 2)))
