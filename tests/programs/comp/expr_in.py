# Result expressions that aren't just tuples of variables.

from incoq.runtime import *

QUERYOPTIONS(
    '{(f(x), y + 1, None) for (x, y) in S}',
    impl = 'inc',
)

S = Set()

def f(y):
    return True

for v1, v2 in [(1, 2), (3, 4)]:
    S.add((v1, v2))

print(sorted({(f(x), y + 1, None) for (x, y) in S}))
