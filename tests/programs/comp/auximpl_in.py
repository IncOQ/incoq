# Implementation based on incremental auxiliary maps only.

from incoq.mars.runtime import *

CONFIG(
    default_impl = 'aux',
)

S = Set()

def main():
    for x, y in [(1, 2), (1, 3), (2, 3), (2, 4), (4, 5)]:
        S.add((x, y))
    a = 1
    print(sorted(QUERY('Q', {(c,) for (a2, b) in S for (b2, c) in S
                                  if a == a2 if b == b2})))

if __name__ == '__main__':
    main()
