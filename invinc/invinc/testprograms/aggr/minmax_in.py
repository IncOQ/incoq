# Min/max query.

from runtimelib import *

OPTIONS(
    default_impl = 'inc',
)

R = Set()

for x in [1, 2, 3, 4, 5]:
    R.add(x)

R.remove(5)

print(min(R))
print(max(R))

for x in [1, 2, 3, 4]:
    R.remove(x)
