from invinc.runtime import *
E = Set()
S = Set()
for (v1, v2) in {(1, 1), (1, 2), (1, 3), (2, 3), (3, 4)}:
    E.add((v1, v2))
S.add(1)
print(sorted({x for (x, x) in E for x in S if (x in S)}))