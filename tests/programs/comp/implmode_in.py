# Alternative implementation strategies for comprehensions.

from incoq.runtime import *

E = Set()

for v1, v2 in {(1, 2), (2, 3), (3, 4), (4, 5)}:
    E.add((v1, v2))

QUERYOPTIONS(
    '{(x, z) for (x, y) in E for (y2, z) in E if y == y2 if z > 1}',
    impl = 'batch',
)
print(sorted({(x, z) for (x, y) in E for (y2, z) in E if y == y2 if z > 1}))

QUERYOPTIONS(
    '{(x, z) for (x, y) in E for (y2, z) in E if y == y2 if z > 2}',
    impl = 'auxonly',
)
print(sorted({(x, z) for (x, y) in E for (y2, z) in E if y == y2 if z > 2}))

QUERYOPTIONS(
    '{(x, z) for (x, y) in E for (y2, z) in E if y == y2 if z > 3}',
    impl = 'inc',
    maint_impl = 'batch',
)
print(sorted({(x, z) for (x, y) in E for (y2, z) in E if y == y2 if z > 3}))

QUERYOPTIONS(
    '{(x, z) for (x, y) in E for (y2, z) in E if y == y2 if z > 4}',
    impl = 'inc',
    maint_impl = 'auxonly',
)
print(sorted({(x, z) for (x, y) in E for (y2, z) in E if y == y2 if z > 4}))
