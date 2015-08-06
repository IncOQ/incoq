# Should ideally generate code that tests if the sets are
# non-empty, without having to iterate over the sets.

from incoq.runtime import *

OPTIONS(
    obj_domain = False,
)

S = Set()
T = Set()

S.add(1)
T.add(2)

print({True for x in S for y in T})
