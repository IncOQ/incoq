# Comprehensions with tuples on enum LHS, in the object domain.

from oinc.runtime import *

OPTIONS(
    obj_domain = True,
)

QUERYOPTIONS(
    '{a for (a, b) in s if a > 1}',
    impl = 'dem',
)

s = Set()

for x, y in [(1, 2), (2, 3), (3, 4)]:
    s.add((x, y))

print(sorted({a for (a, b) in s if a > 1}))
