# Comprehensions with constants and globals.

from runtimelib import *

OPTIONS(
    obj_domain = True,
)


s = Set()
for i in [1, 2, 3]:
    o = Obj()
    o.i = i
    s.add(o)

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

print(sorted({o.i + 1 for o in s}))
print({None for o in s})
