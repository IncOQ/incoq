# Another test of augmented self-join code with demand.
# Demand invariants should be maintained in a correct order
# for demand propagation. When turning normal clauses into
# filtered ones, augmented clauses should become non-augmented
# and non-augmented should become subtractive.

from runtimelib import *

OPTIONS(
    selfjoin_strat = 'aug',
)

QUERYOPTIONS(
    '{z for (x, x2) in E for (x3, y) in E for (y2, z) in S if x == x2 if x2 == x3 if y == y2}',
    impl = 'dem',
    uset_force = True,
)

E = Set()
S = Set()

# Query once to demand it so the below addition updates cause maintenance.
print(sorted({z for (x, x2) in E for (x3, y) in E for (y2, z) in S
                if x == x2 if x2 == x3 if y == y2}))

# Note that we're adding to S first so E will double join with
# it if done incorrectly.
S.add((1, 2))
E.add((1, 1))

print(sorted({z for (x, x2) in E for (x3, y) in E for (y2, z) in S
                if x == x2 if x2 == x3 if y == y2}))

S.remove((1, 2))

# If we screwed up our reference counts, we won't get the right answer.
print(sorted({z for (x, x2) in E for (x3, y) in E for (y2, z) in S
                if x == x2 if x2 == x3 if y == y2}))
