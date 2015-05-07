# Nested object-domain comprehensions.

from incoq.runtime import *

OPTIONS(
    obj_domain = True,
)

QUERYOPTIONS(
    '{x for x in s if x.a > 1}',
    uset_mode = 'none',
    impl = 'inc',
)

QUERYOPTIONS(
    '{y.b for y in {x for x in s if x.a > 1}}',
    uset_mode = 'none',
    impl = 'inc'
)

s = Set()

for i in [1, 2, 3]:
    o = Obj()
    o.a = i
    o.b = i * 2
    s.add(o)

print(sorted({y.b for y in {x for x in s if x.a > 1}}))
