# Auxmaps with equality constraints.

from runtimelib import *

P = Set()

for v in [(1, 2, 2), (2, 2, 2), (3, 3, 3), (4, 1, 2),
          (5, 2, 3), (9, 9, 9)]:
    P.add(v)

P.remove((9, 9, 9))

print(sorted(setmatch(P, 'uu2', ())))
print(sorted(setmatch(P, 'ub2', 2)))
