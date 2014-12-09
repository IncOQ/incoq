# Aggregates over sets of tuples.

from runtimelib import *

OPTIONS(
    default_impl = 'inc',
)

R = Set()

for (x, y, z) in [(1, 2, 3), (1, 4, 5), (6, 7, 8)]:
    R.add((x, y, z))

a = 1
print(count(R))
print(count(setmatch(R, 'buu', a)))
