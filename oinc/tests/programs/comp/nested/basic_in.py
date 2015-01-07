# Nested comprehensions.

from oinc.runtime import *

QUERYOPTIONS(
    '{(a, c) for (a, b) in E for (b2, c) in E if b == b2}',
    impl = 'inc',
)

QUERYOPTIONS(
    '{(x, z) for (x, y) in E for (y2, z) in {(a, c) for (a, b) in E for (b2, c) in E if b == b2} if y == y2}',
    impl = 'inc'
)

E = Set()

for v1, v2 in [(1, 2), (2, 3), (3, 4), (4, 5)]:
    E.add((v1, v2))

print(sorted({(x, z) for (x, y) in E
                     for (y2, z) in {(a, c) for (a, b) in E for (b2, c) in E if b == b2}
                     if y == y2}))
