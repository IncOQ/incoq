# Basic comprehension incrementalization test.

from incoq.mars.runtime import *

SYMCONFIG('Q',
    impl = 'inc',
)

S = Set()

def main():
    for x, y in [(1, 2), (1, 3), (2, 3), (2, 4)]:
        S.add((x, y))
    print(sorted(QUERY('Q', {(c,) for (a, b) in S for (b2, c) in
                                  S if b == b2})))
    S.clear()
    print(sorted(QUERY('Q', {(c,) for (a, b) in S for (b2, c) in S
                                  if b == b2})))

if __name__ == '__main__':
    main()
