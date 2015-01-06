# Demand, with the augmented self-join strategy.
# Demand invariant maintenance should still come before
# query maintenance at additions and after it at removals.

from oinc.runtime import *

OPTIONS(
    selfjoin_strat = 'aug',
)

QUERYOPTIONS(
    '{z for (x, y) in E for (y2, z) in E if y == y2}',
    params = ['x'],
    impl = 'dem',
    uset_force = False,
)

E = Set()

for a, b in {(1, 2), (2, 3), (2, 4)}:
    E.add((a, b))

x = 1

print(sorted({z for (x, y) in E for (y2, z) in E if y == y2}))
