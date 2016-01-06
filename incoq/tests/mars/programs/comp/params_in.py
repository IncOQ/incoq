# Comprehension with parameters.

from incoq.mars.runtime import *

SYMCONFIG('Q',
    impl='inc',
)

S = Set()

def main():
    for x, y in [(1, 2), (2, 3), (3, 4)]:
        S.add((x, y))
    a = 1
    print(QUERY('Q', {b for (a2, b) in S if a == a2}))

if __name__ == '__main__':
    main()
