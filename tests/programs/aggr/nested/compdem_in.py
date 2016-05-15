# Demand-driven comprehension with an aggregate.

from incoq.runtime import *

OPTIONS(
    default_impl = 'inc',
)

S = Set()
E = Set()

for e in [1, 2, 3, 4]:
    S.add(e)

for e in [(1, 5), (1, 8), (1, 15), (2, 9), (2, 18)]:
    E.add(e)

QUERYOPTIONS(
    '{y for x2, y in E if x2 == x if y < sum(S)}',
    impl = 'dem',
    uset_mode = 'all',
)

x = 1
print(sorted({y for x2, y in E if x2 == x if y < sum(S)}))
