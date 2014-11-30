# Test comprehension occurrences that don't try to add
# to the demand set.

from runtimelib import *

QUERYOPTIONS(
    '{z for (x, y) in E for (y2, z) in E if y == y2}',
    params = ['x'],
    uset_mode = 'all',
    impl = 'inc',
)

E = Set()

for a, b in {(1, 2), (2, 3), (2, 4)}:
    E.add((a, b))

x = 1

print(sorted({z for (x, y) in E for (y2, z) in E if y == y2}))

print(sorted(NODEMAND({z for (x, y) in E for (y2, z) in E if y == y2})))
