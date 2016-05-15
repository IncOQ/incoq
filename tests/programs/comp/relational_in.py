# Non-relational flat comprehensions.

from incoq.runtime import *

CONFIG(
    default_impl = 'inc',
)

S = Set()
R = Set()

def main():
    for x, y in [(1, 2), (1, 3), (2, 3), (2, 4), (3, 5)]:
        S.add((x, y))
        if x not in R:
            R.add(x)
    print(sorted(QUERY('Q', {c for (a, b) in S if a in R for (b2, c) in S
                               if b == b2})))
    R.remove(1)
    print(sorted(QUERY('Q', {c for (a, b) in S if a in R for (b2, c) in S
                               if b == b2})))

if __name__ == '__main__':
    main()
