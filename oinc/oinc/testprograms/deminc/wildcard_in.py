# Make sure demand filtering for clauses with wildcards works.

from runtimelib import *

QUERYOPTIONS(
    '{b for (a2, b) in R for (b2, _) in R if a == a2 if b == b2}',
    impl = 'dem',
    uset_force = True,
)

R = Set()

for x, y in [(1, 2), (2, 3), (3, 4)]:
    R.add((x, y))

a = 1
print(sorted({b for (a2, b) in R for (b2, _) in R
                if a == a2 if b == b2}))
