from incoq.runtime import *

QUERYOPTIONS(
    '''{x for x in S for (x2, x3, y4) in E
                if x == x2 if x2 == x3}
    ''',
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

print(sorted({x for x in S for (x2, x3, y4) in E
                if x == x2 if x2 == x3}))

E.remove((1, 1, 'a'))
E.remove((2, 2, 'b'))

print(sorted({x for x in S for (x2, x3, y4) in E
                if x == x2 if x2 == x3}))
