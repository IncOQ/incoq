# Make sure If clauses get converted before pair domain transformation.
# If this doesn't happen, the query will look ok at the end but the
# maintenance code won't be inserted.

from runtimelib import *

OPTIONS(
    obj_domain = True,
)

s1 = Set()
s2 = Set()
t = Set()
for i in {1, 2, 3, 4, 5}:
    o = Obj()
    o.i = i
    if i % 2:
        s1.add(o)
    else:
        s2.add(o)
    t.add(o)

QUERYOPTIONS(
    '{o.i for o in s if o in t}',
    params = ['s', 't'],
    impl = 'inc',
    uset_mode = 'none',
)
s = s1
print(sorted({o.i for o in s if o in t}))
s = s2
print(sorted({o.i for o in s if o in t}))
