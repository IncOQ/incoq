# Output as relations rather than objects.

from invinc.runtime import *

OPTIONS(
    obj_domain = True,
    obj_domain_out = False,
)

s1 = Set()
s2 = Set()
for i in range(1, 5):
    o = Obj()
    o.i = i
    if i % 2:
        s1.add(o)
    else:
        s2.add(o)

QUERYOPTIONS(
    '{o.i for o in s}',
    params = ['s'],
    impl = 'inc',
)
s = s1
print(sorted({o.i for o in s}))
s = s2
print(sorted({o.i for o in s}))
