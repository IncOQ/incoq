# Aggregate of a lookup.

from runtimelib import *

OPTIONS(
    default_impl = 'inc',
)

R = Set()

for x in [('A', 1), ('A', 2), ('A', 3), ('B', 4), ('B', 5)]:
    R.add(x)

R.remove(('B', 5))

k = 'A'
print(sum(setmatch(R, 'bu', k)))
