# Dead-code elimination.

from incoq.runtime import *

OPTIONS(
    deadcode_keepvars = ['S'],
)

R = Set()
S = Set()
T = Set()

for x, y in [(1, 2), (1, 3), (2, 3), (1, 4)]:
    R.add((x, y))
    S.add((x, y))
    T.add((x, y))

R.remove((1, 4))
S.remove((1, 4))
T.remove((1, 4))

print(sorted(R))
