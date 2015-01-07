# Test conversion to runtimelib types.

from oinc.runtime import *

QUERYOPTIONS(
    '{x.a for x in S}',
    impl = 'inc',
)
QUERYOPTIONS(
    '{x.b for x in S}',
    impl = 'batch',
)

class T:
    def __init__(self, v):
        self.a = v
        self.b = 0

S = set()
for elem in {T(1), T(2), T(3)}:
    S.add(elem)

print(sorted({x.a for x in S}))

print(sorted({x.b for x in S}))
