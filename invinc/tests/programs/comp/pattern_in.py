# Disable pattern conversion (input and output both have patterns).
# No output text file because program is not executable as Python code.

from invinc.runtime import *

OPTIONS(
    pattern_in = True,
    pattern_out = True,
)

E = Set()
S = Set()

for v1, v2 in {(1, 1), (1, 2), (1, 3), (2, 3), (3, 4)}:
    E.add((v1, v2))

S.add(1)

print(sorted({x for (x, x) in E for x in S if x in S}))
