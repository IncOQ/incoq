# Nested comprehensions with demand.

from incoq.mars.runtime import *

CONFIG(
    default_impl = 'inc',
)

S = Set()

def main():
    for x in [1, 2, 3, 4, 5]:
        S.add((x,))
    k = 2
    j = 4
    print(sorted(QUERY('Q2', {(b,) for (b,) in QUERY('Q1',
                                   {(a,) for (a,) in S if a >= k})
                                if b <= j})))

if __name__ == '__main__':
    main()
