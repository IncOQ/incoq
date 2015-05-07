# Aggregate of a field retrieval in a comprehension.

from incoq.runtime import *

OPTIONS(
    obj_domain = True,
    default_impl = 'inc',
)
QUERYOPTIONS(
    '{sum(o.f) for o in s}',
    params = ['s'],
    impl = 'dem',
)

s = Set()
for x in [1, 2, 3]:
    o = Obj()
    o.f = Set()
    for y in [10, 20, 30]:
        o.f.add(x * y)
    s.add(o)

print(sorted({sum(o.f) for o in s}))
