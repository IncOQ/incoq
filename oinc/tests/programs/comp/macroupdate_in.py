# Make sure macro updates are handled.

from oinc.runtime import *

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
R = Set()
T = Set()
V = Set()

for v1, v2 in [(1, 2), (1, 3), (2, 3), (3, 4)]:
    R.add((v1, v2))

T.add((3, 4))
V.add((5, 5))

def query():
    print(sorted({x for (x, y) in E if f(y)}))
    print(sorted({(x, z) for (x, y) in E for (y2, z) in E if y == y2}))

E.update(R)
query()
E.difference_update(T)
query()
E.symmetric_difference_update(V)
query()
E.intersection_update(V)
query()

