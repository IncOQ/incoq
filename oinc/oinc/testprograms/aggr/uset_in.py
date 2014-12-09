# Aggregate of a comprehension with a U-set.

from runtimelib import *

OPTIONS(
    default_impl = 'inc',
)

QUERYOPTIONS(
    '{y for (x2, y) in E if x == x2 if y < L}',
    uset_mode = 'explicit',
    uset_params = ['L'],
)

E = Set()

for e in [(1, 2), (1, 3), (1, 15), (2, 4)]:
    E.add(e)

L = 10
x = 1
print(sum({y for (x2, y) in E if x == x2 if y < L}))
E.remove((1, 3))
print(sum({y for (x2, y) in E if x == x2 if y < L}))
