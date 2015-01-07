# Comprehension with a demand-driven aggregate.

from invinc.runtime import *

OPTIONS(
    default_impl = 'inc',
)

S = Set()
E = Set()

for e in [1, 2, 4, 8]:
    S.add(e)

for e in [(1, 2), (1, 3), (2, 1), (3, 4), (8, 1), (8, 4)]:
    E.add(e)

QUERYOPTIONS(
    '{y for x2, y in E if x2 == x}',
    uset_mode = 'all',
    impl = 'dem',
)

QUERYOPTIONS(
    '{x for x in S if x < sum({y for x2, y in E if x2 == x})}',
    impl = 'dem',
)

print(sorted({x for x in S if x < sum({y for x2, y in E if x2 == x})}))

