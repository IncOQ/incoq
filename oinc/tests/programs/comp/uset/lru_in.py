# LRU cache on a U-set.

from runtimelib import *

E = Set()

for v1, v2 in [(1, 2), (2, 3), (2, 4), (4, 5)]:
    E.add((v1, v2))

QUERYOPTIONS(
    '{z for (x2, y) in E for (y2, z) in E if x == x2 if y == y2}',
    params = ['x'],
    uset_mode = 'all',
    uset_lru = 2,
    impl = 'inc',
)

# Tracing the execution of this loop, it should be the case that 1 and 2
# get added, then 1 is pinged, then when 3 is added 2 is removed, then
# 1 is pinged again.
for x in [1, 2, 1, 3, 1]:
    print(sorted({z for (x2, y) in E for (y2, z) in E if x == x2 if y == y2}))
