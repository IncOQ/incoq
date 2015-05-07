# Aggregate half-demand strategy.

from incoq.runtime import *

OPTIONS(
    default_impl = 'dem',
    default_aggr_halfdemand = True,
)

S = Set()
R = Set()

print(sum(R))

for e in [1, 2]:
    R.add(e)

for e in [1, 5, 15, 20]:
    S.add(e)

print(sum(R))

for e in [3, 4]:
    R.add(e)

print(sorted({x for x in S if x > sum(R)}))

for e in [1, 2, 3, 4]:
    R.remove(e)

print(sorted({x for x in S if x > sum(R)}))
