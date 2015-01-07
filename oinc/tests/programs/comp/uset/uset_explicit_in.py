# Incrementalized comprehensions with U-set.

from oinc.runtime import *

R = Set()

for v1, v2, v3 in {(1, 2, 3), (2, 2, 3), (1, 3, 4)}:
    R.add((v1, v2, v3))

a = 1
b = 2

QUERYOPTIONS(
    '{c for (a2, b2, c) in R if a == a2 if b == b2}',
    params = ['a', 'b'],
    uset_mode = 'explicit',
    uset_params = ['a'],
    impl = 'inc',
)
print(sorted({c for (a2, b2, c) in R if a == a2 if b == b2}))
