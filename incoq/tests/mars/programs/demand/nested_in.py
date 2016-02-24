# Filtering nested comprehensions.

from incoq.mars.runtime import *

SYMCONFIG('Q1',
    impl = 'inc',
)
SYMCONFIG('Q2',
    impl = 'filtered',
)

S = Set()
T = Set()

def main():
    for x, y in [(1, 1), (1, 2), (2, 2), (2, 3)]:
        S.add((x, y))
    T.add((3,))
    print(sorted(unwrap(QUERY('Q2', {(w,) for (v,) in QUERY('Q1',
                                          {(a,) for (a, b) in S if a == b})
                                          for (v2, w) in S if v == v2
                                          if (w,) in T}))))

if __name__ == '__main__':
    main()
