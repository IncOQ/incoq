# Unconstrained parameters that force a batch recomputation when updated.

from invinc.runtime import *

E = Set()

for v1, v2 in [(1, 2), (2, 3), (3, 4), (4, 5)]:
    E.add((v1, v2))

QUERYOPTIONS(
    '{z for (x, y) in E for (y2, z) in E if y == y2 if low <= x <= high}',
    params = ['low', 'high'],
    noninc_params = ['low', 'high'],
    impl = 'inc',
)

low = 1
high = 3
print(sorted({z for (x, y) in E for (y2, z) in E if y == y2 if low <= x <= high}))

high = 2
print(sorted({z for (x, y) in E for (y2, z) in E if y == y2 if low <= x <= high}))
