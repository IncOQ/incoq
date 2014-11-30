# Inline comp maintenance.

from runtimelib import *

OPTIONS(
    maint_inline = True,
)

QUERYOPTIONS(
    '{x for (x, y) in E if f(y)}',
    impl = 'inc',
)
QUERYOPTIONS(
    '{(x, z) for (x, y) in E for (y2, z) in E if y == y2}',
    impl = 'inc',
)

def f(y):
    return True

E = Set()

for v1, v2 in {(1, 2), (1, 3), (2, 3), (3, 4)}:
    E.add((v1, v2))

print(sorted({x for (x, y) in E if f(y)}))

print(sorted({(x, z) for (x, y) in E for (y2, z) in E if y == y2}))
