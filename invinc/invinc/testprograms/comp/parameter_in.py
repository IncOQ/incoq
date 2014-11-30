# Comprehensions with parameters.

from runtimelib import *

E = set()

for v1, v2 in {(1, 2), (2, 3), (2, 4), (4, 5)}:
    E.add((v1, v2))

x = 1
y = 5
QUERYOPTIONS(
    '{z for (x2, y) in E for (y2, z) in E if x == x2 if y == y2}',
    params = ['x'],
)
print(sorted({z for (x2, y) in E for (y2, z) in E if x == x2 if y == y2}))

QUERYOPTIONS(
    '{y for (x2, y) in E if x == x2}',
    params = ['x'],
    impl = 'auxonly',
)
print(sorted({y for (x2, y) in E if x == x2}))

QUERYOPTIONS(
    '{(x, y) for (x, y2) in E if y == y2}',
    params = ['y'],
    impl = 'inc',
)
print(sorted({(x, y) for (x, y2) in E if y == y2}))
