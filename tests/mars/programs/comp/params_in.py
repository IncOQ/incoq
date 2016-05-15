# Comprehension with parameters.

from incoq.mars.runtime import *

CONFIG(
    default_impl = 'inc',
)

S = Set()

def main():
    for x, y in [(1, 2), (2, 3), (3, 4)]:
        S.add((x, y))
    a = 1
    # We write "a2 == a" instead of "a == a2" so that this test will
    # fail if we don't correctly infer that a is a parameter.
    print(sorted(QUERY('Q', {(b,) for (a2, b) in S if a2 == a})))
    S.clear()
    print(sorted(QUERY('Q', {(b,) for (a2, b) in S if a2 == a})))

if __name__ == '__main__':
    main()
