# Comprehensions with result expressions that are not just
# simple variables.

from oinc.runtime import *

OPTIONS(
    obj_domain = True,
)

QUERYOPTIONS(
    '{o.i + 1 for o in s}',
    params = ['s'],
    uset_mode = 'none',
    impl = 'inc',
)

QUERYOPTIONS(
    '{None for o in s}',
    params = ['s'],
    uset_mode = 'none',
    impl = 'inc',
)

s = Set()
for i in [1, 2, 3]:
    o = Obj()
    o.i = i
    s.add(o)

print(sorted({o.i + 1 for o in s}))
print({None for o in s})
