# Comprehension with non-enumvar parameter, which should be
# automatically added to a U-set.

from incoq.runtime import *

E = Set()
g = 1

for z in [1, 2, 3]:
    E.add(z)

QUERYOPTIONS(
    '{x for x in E if x > g}',
    impl = 'inc',
)
print(sorted({x for x in E if x > g}))
