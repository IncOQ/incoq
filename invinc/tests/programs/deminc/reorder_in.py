# Reorder the clauses for generating the demand graph.

from invinc.runtime import *

QUERYOPTIONS(
    '{x for (x, y) in E for (y2, z2) in E if y == y2 if z == z2}',
    params = ['z'],
    impl = 'dem',
    uset_force = False,
    demand_reorder = [1, 0]
)

E = Set()

for a, b in {(1, 3), (2, 3), (3, 4)}:
    E.add((a, b))

z = 4

print(sorted({x for (x, y) in E for (y2, z2) in E if y == y2 if z == z2}))
