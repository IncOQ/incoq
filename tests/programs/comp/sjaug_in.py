# Self-joins using augmented clauses.

from incoq.runtime import *

OPTIONS(
    selfjoin_strat = 'aug',
)

QUERYOPTIONS(
    '{z for (x, x2) in E for (x3, y) in E for (y2, z) in S if x == x2 if x2 == x3 if y == y2}',
    impl = 'inc',
)

E = Set()
S = Set()

# If the reference counts get bungled due to double-counting on E.add,
# we should see an erroneous non-empty result.
S.add((1, 2))
E.add((1, 1))
S.remove((1, 2))

print(sorted({z for (x, x2) in E for (x3, y) in E for (y2, z) in S
                if x == x2 if x2 == x3 if y == y2}))
