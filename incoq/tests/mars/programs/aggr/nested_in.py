# Aggregate sandwiched between comprehensions.

from incoq.mars.runtime import *

SYMCONFIG('Q1',
    impl = 'inc',
)
SYMCONFIG('Q2',
    impl = 'inc',
)
SYMCONFIG('Q3',
    impl = 'inc',
)

S = Set()

def main():
    # Find all two-hop path destinations, where the first step takes
    # the smallest node available.
    for a, b in [(1, 2), (2, 3), (2, 4), (1, 3), (3, 5)]:
        S.add((a, b))
    
    x = 1
    print(sorted(QUERY('Q3', {z for (x2, y) in S for (y2, z) in S
                                if x == x2 if y == y2
                 if (y,) <= QUERY('Q2', min(QUERY('Q1',
                                  {(w,) for (x3, w) in S if x3 == x})))})))


if __name__ == '__main__':
    main()
