# Aggregate rewriting.

from incoq.runtime import *

OPTIONS(
    default_impl = 'inc',
    obj_domain = True,
)

R = Set()
R.add(1)
print(sum(R))

# These forms don't get transformed.
print(sum({1, 2}))
print(sum([1, 2]))
print(sum(({1:1}[1], 2)))
