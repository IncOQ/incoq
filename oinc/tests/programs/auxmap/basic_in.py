# Basic auxiliary map usage.

from oinc.runtime import *

R = Set()

for x, y in [(1, 2), (1, 3), (2, 3), (1, 4)]:
    R.add((x, y))

R.remove((1, 4))

print(sorted(R))
print(sorted(setmatch(R, 'bu', 1)))
print(sorted(setmatch(R, 'ub', 2)))
