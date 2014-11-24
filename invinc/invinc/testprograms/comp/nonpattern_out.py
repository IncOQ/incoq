from runtimelib import *
E = set()
S = set()
for (v1, v2, z) in {(1, 1, 'a'), (1, 2, 'b'), (1, 3, 'c'), (2, 3, 'd'), (3, 4, 'e')}:
    E.add((v1, v2, z))
S.add(1)
print(sorted({x for (x, x2, c) in E if (x2 in S) if (x == x2)}))