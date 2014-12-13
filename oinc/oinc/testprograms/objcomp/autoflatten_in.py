# Only run object domain conversion when necessary.
# Don't include input relations as parameters.

from runtimelib import *

OPTIONS(
    obj_domain = True,
    autodetect_input_rels = True,
)


R = Set()
for i in range(1, 5):
    R.add(i)

QUERYOPTIONS(
    '{x for x in R}',
    uset_mode = 'none',
    impl = 'inc',
)

print(sorted({x for x in R}))
R.remove(3)
print(sorted({x for x in R}))

# Don't M-flatten since the M-set is never used.
# Test this with an update to a set that can't be
# classified as a relation due to aliasing.
S = Set()
# This should even be eliminated as dead code.
s = S
s.add(1)

# Don't F-flatten objects since they're not used.
o = Obj()
o.a = 1
