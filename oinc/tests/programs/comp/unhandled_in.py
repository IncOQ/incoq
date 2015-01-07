# Programs with comprehensions that we don't handle.

from oinc.runtime import *

OPTIONS(
    default_impl = 'inc',
)

N = Set()

for i in range(3):
    N.add(i)

print(sorted({(x, y) for x in N for y in N}))

print(sorted({(x, y) for x in range(3) for y in range(3)}))
