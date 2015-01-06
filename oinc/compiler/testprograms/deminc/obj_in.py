# Basic tag-based demand incrementalization.

from runtimelib import *

OPTIONS(
    obj_domain = True,
)

QUERYOPTIONS(
    '{x.a for x in S}',
    params = ['S'],
    uset_mode = 'all',
    impl = 'dem',
)

S = Set()
o = Obj()
o.a = 1
S.add(o)

print(sorted({x.a for x in S}))
