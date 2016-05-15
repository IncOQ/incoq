# Aggregate of a variable in the object domain.

from incoq.runtime import *

OPTIONS(
    obj_domain = True,
    default_impl = 'inc',
)
QUERYOPTIONS(
    'sum(s)',
    params = ['s'],
    impl = 'dem',
)
QUERYOPTIONS(
    'sum(o.f)',
    params = ['o'],
    impl = 'dem',
)

r = Set()
t = Set()
o = Obj()
o.f = t

for x in [1, 2, 3, 4, 5]:
    r.add(x)
    t.add(x)

r.remove(5)

s = r
print(sum(s))
print(sum(o.f))
