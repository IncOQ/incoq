# Incrementalized comprehension with setmatch.

from oinc.runtime import *

QUERYOPTIONS(
    '{(x, z) for (x, y) in E for (y2, z) in E if y == y2}',
    impl = 'inc',
)

E = Set()

for v1, v2 in {(1, 2), (1, 3), (2, 3), (3, 4)}:
    E.add((v1, v2))

p = 1
print(sorted(setmatch({(x, z) for (x, y) in E for (y2, z) in E if y == y2},
                      'bu', p)))
