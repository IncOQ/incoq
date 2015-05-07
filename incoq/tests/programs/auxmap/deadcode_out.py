from incoq.runtime import *
R = Set()
S = Set()
for (x, y) in [(1, 2), (1, 3), (2, 3), (1, 4)]:
    R.add((x, y))
    S.add((x, y))
R.remove((1, 4))
S.remove((1, 4))
print(sorted(R))