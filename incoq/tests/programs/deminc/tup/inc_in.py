# Comprehensions with nested tuples, incremental.

from incoq.runtime import *

QUERYOPTIONS(
    '{e for (a2, (b, c)) in R for (b2, (d, e)) in R if a2 == a if b2 == b}',
    impl = 'dem',
    uset_force = True,
)

R = Set()

for x, y in [(1, (2, 3)), (2, (3, 4)), (3, (4, 5))]:
    R.add((x, y))

a = 1
print(sorted({e for (a2, (b, c)) in R for (b2, (d, e)) in R
                if a2 == a if b2 == b}))
