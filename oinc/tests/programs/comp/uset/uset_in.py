# Incrementalized comprehensions with U-set.

from oinc.runtime import *

E = Set()

for v1, v2 in {(1, 2), (2, 3), (2, 4), (4, 5)}:
    E.add((v1, v2))

x = 1

QUERYOPTIONS(
    '{z for (x2, y) in E for (y2, z) in E if x == x2 if y == y2}',
    params = ['x'],
    uset_mode = 'all',
    impl = 'inc',
)
print(sorted({z for (x2, y) in E for (y2, z) in E if x == x2 if y == y2}))
