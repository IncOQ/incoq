from incoq.runtime import *

QUERYOPTIONS(
    '''
    {x for x in S for x2 in {z1 for (z1, z2, y) in E
                                         if z1 == x if z1 == z2}
                if x == x2}
    ''',
    uset_force = True,
    uset_mode = 'all',
)

QUERYOPTIONS(
    '{z1 for (z1, z2, y) in E if z1 == x if z1 == z2}',
    uset_force = True,
    uset_mode = 'all',
)

S = Set()
E = Set()

for a in [1, 2, 3]:
    S.add(a)
for a, b, c in [(1, 1, 'a'), (1, 2, 'b'), (2, 2, 'b'), (2, 3, 'a'),
                (2, 2, 'c'), (3, 3, 'c')]:
    E.add((a, b, c))

print(sorted({x for x in S for x2 in {z1 for (z1, z2, y) in E
                                         if z1 == x if z1 == z2}
                if x == x2}))

E.remove((1, 1, 'a'))
E.remove((2, 2, 'b'))

print(sorted({x for x in S for x2 in {z1 for (z1, z2, y) in E
                                         if z1 == x if z1 == z2}
                if x == x2}))
