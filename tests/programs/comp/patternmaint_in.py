# Comprehension whose maintenance requires auxmaps for equalities
# and wildcards.

from incoq.runtime import *

QUERYOPTIONS(
    '{x for (x, x2, y, z) in P if y in S if x == x2}',
    impl = 'inc',
)

P = Set()
S = Set()

for v in {(1, 1, 2, 3), (1, 2, 2, 4)}:
    P.add(v)

S.add(2)

print(sorted({x for (x, x2, y, z) in P if y in S
                if x == x2}))
