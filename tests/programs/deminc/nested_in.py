# Nested comprehensions with demand.

from incoq.runtime import *

QUERYOPTIONS(
    '{(a2, c) for (a2, b) in E for (b2, c) in E if a == a2 if b == b2}',
    impl = 'inc',
    uset_mode = 'all',
)

QUERYOPTIONS(
    '{(x, z) for (x, y) in E for (y2, z) in {(a2, c) for (a2, b) in E for (b2, c) in E if a == a2 if b == b2} if y == y2}',
    impl = 'dem',
    # Use default of uset_mode = 'uncon',
    # test that "a" is picked up as unconstrained.
)

E = Set()

for v1, v2 in [(1, 2), (2, 3), (3, 4), (4, 5)]:
    E.add((v1, v2))

def query(a):
    print(sorted({(x, z) for (x, y) in E
                         for (y2, z) in {(a2, c) for (a2, b) in E for (b2, c) in E if a == a2 if b == b2}
                         if y == y2}))

query(2)
E.remove((1, 2))
query(2)
