# Basic incrementalized comprehensions.

from runtimelib import *

OPTIONS(
    default_impl = 'inc',
)

QUERYOPTIONS(
    '{x for x in S if x > sum(R)}',
    impl = 'dem',
)

S = Set()
R = Set()

for e in [1, 5, 15, 20]:
    S.add(e)

for e in [1, 2, 3, 4]:
    R.add(e)

print(sorted({x for x in S if x > sum(R)}))

for e in [1, 2, 3, 4]:
    R.remove(e)

print(sorted({x for x in S if x > sum(R)}))
