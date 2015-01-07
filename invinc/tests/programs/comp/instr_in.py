# Basic incrementalized comprehensions.

from invinc.runtime import *

OPTIONS(
    default_impl = 'inc',
    default_instrument = True,
)

def f(y):
    return True

E = Set()

for v1, v2 in [(1, 2), (2, 3)]:
    E.add((v1, v2))

print(sorted({x for (x, y) in E if f(y)}))
