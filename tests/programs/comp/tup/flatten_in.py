# Check for flattening of relations that use nested tuples.

from incoq.runtime import *

OPTIONS(
    flatten_rels = ['R'],
    default_impl = 'inc',
)

R = Set()
S = Set()

R.update([(1, (2, 3)), (4, (5, 6))])
S.update([1, 4])

print(sorted({z for (x, (y, z)) in R if x in S}))
