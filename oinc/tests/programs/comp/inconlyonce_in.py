# Don't incrementalize the same comp more than once if we can
# avoid it.

from oinc.runtime import *

QUERYOPTIONS(
    '{x for (x, y) in E}',
    impl = 'inc',
)

E = Set()

for v1, v2 in [(1, 2), (1, 3), (2, 3), (3, 4)]:
    E.add((v1, v2))

print(sorted({x for (x, y) in E}))
print(sorted({x for (x, y) in E}))
