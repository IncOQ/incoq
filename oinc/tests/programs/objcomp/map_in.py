# Map object-domain conversion.

from oinc.runtime import *

OPTIONS(
    obj_domain = True,
)

m = Map()
s1 = Set()
s2 = Set()
m['a'] = s1
m['b'] = s2

for i in range(10):
    o = Obj()
    o.i = i
    if i % 2:
        s1.add(o)
    else:
        s2.add(o)

QUERYOPTIONS(
    '{o.i for o in m[k]}',
    params = ['m', 'k'],
    uset_mode = 'none',
    impl = 'inc',
)

k = 'a'
print(sorted({o.i for o in m[k]}))
k = 'b'
print(sorted({o.i for o in m[k]}))
