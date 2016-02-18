# Aggregate of a comprehension, no demand.

from incoq.mars.runtime import *

SYMCONFIG('Q1',
    impl = 'inc',
)
SYMCONFIG('Q2',
    impl = 'inc',
)

S = Set()

def main():
    for x, y in [(1, 2), (2, 3), (2, 4), (3, 4)]:
        S.add((x, y))
    a = 1
    print(QUERY('Q2', sum(unwrap(QUERY('Q1', {(b,) for (a2, b) in S
                                                   if a2 == a})))))
    a = 0
    print(QUERY('Q2', sum(unwrap(QUERY('Q1', {(b,) for (a2, b) in S
                                                   if a2 == a})))))
    a = 2
    print(QUERY('Q2', sum(unwrap(QUERY('Q1', {(b,) for (a2, b) in S
                                                   if a2 == a})))))
    S.remove((2, 4))
    print(QUERY('Q2', sum(unwrap(QUERY('Q1', {(b,) for (a2, b) in S
                                                   if a2 == a})))))
    S.clear()
    print(QUERY('Q2', sum(unwrap(QUERY('Q1', {(b,) for (a2, b) in S
                                                   if a2 == a})))))

if __name__ == '__main__':
    main()
