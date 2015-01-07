# Aggregate with a LRU cache.

from invinc.runtime import *

OPTIONS(
    default_impl = 'inc',
)

QUERYOPTIONS(
    '{y for (x2, y) in E if x == x2}',
    uset_mode = 'all',
)

QUERYOPTIONS(
    'sum({y for (x2, y) in E if x == x2})',
    uset_lru = 2,
)

E = Set()

for e in [(1, 2), (1, 3), (2, 4), (2, 10), (3, 1)]:
    E.add(e)

# Tracing the execution, 1 and 2 should be added, then 1 should be
# pinged, then 2 should be removed to make way for 3.
for x in [1, 2, 1, 3]:
    print(sum({y for (x2, y) in E if x == x2}))
