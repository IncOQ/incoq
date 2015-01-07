# Aggregate of a comprehension.

from invinc.runtime import *

OPTIONS(
    default_impl = 'inc',
)

E = Set()

for e in [(1, 2), (2, 3), (2, 4), (3, 5)]:
    E.add(e)

x = 1
print(sum({z for (x2, y) in E for (y2, z) in E if x == x2 if y == y2}))
