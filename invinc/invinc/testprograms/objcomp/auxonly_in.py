# Basic object-set comprehension.

from runtimelib import *

OPTIONS(
    obj_domain = True,
)

# Test non-transformation of _add().
N = Set()
for i in range(1, 5):
    N._add(i)

s1 = Set()
s2 = Set()
for i in N:
    o = Obj()
    o.i = i
    if i % 2:
        s1.add(o)
    else:
        s2.add(o)

QUERYOPTIONS(
    '{o.i for o in s}',
    params = ['s'],
    impl = 'auxonly',
)
s = s1
print(sorted({o.i for o in s}))
s = s2
print(sorted({o.i for o in s}))
