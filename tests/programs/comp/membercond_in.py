# Memberships expressed as condition clauses.

from incoq.runtime import *

CONFIG(
    default_impl = 'inc',
)

S = Set()
R = Set()

def main():
    for x, y in [(1, 2), (1, 3), (2, 3), (2, 4)]:
        S.add((x, y))
    R.add((1,))
    print(sorted(QUERY('Q', {(b,) for (a, b) in S if (a,) in R})))

if __name__ == '__main__':
    main()
