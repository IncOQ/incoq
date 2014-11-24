# Disable tag checks.

from runtimelib import *

OPTIONS(
    tag_checks = False,
)

QUERYOPTIONS(
    '{z for (x, y) in E for (y2, z) in E if y == y2}',
    params = ['x'],
    impl = 'dem',
    uset_force = False,
)

E = Set()

for a, b in {(1, 2), (2, 3), (2, 4)}:
    E.add((a, b))

x = 1

print(sorted({z for (x, y) in E for (y2, z) in E if y == y2}))
