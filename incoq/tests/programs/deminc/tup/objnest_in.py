# Nested tuples in membership clauses, in object domain.

from incoq.runtime import *

OPTIONS(
    obj_domain = True,
)

s1 = Set()
for i in [1, 2, 3]:
    s1.add(((i, 2*i), 3*i))
    s1.add(((2*i, 3*i), 4*i))

QUERYOPTIONS(
    '{x for ((x, y), z) in s if x + y == z}',
    params = ['s'],
    impl = 'dem',
)
s = s1
print(sorted({x for ((x, y), z) in s if x + y == z}))
