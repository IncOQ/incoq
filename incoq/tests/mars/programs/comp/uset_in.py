# Comprehension with unconstrained parameters.

from incoq.mars.runtime import *

SYMCONFIG('Q',
    impl = 'inc',
)

S = Set()

def main():
    for v in [1, 3]:
        S.add((v,))
    a = 2
    print(QUERY('Q', {x for (x,) in S if x > a}))
    for v in [2, 4]:
        S.add((v,))
    print(QUERY('Q', {x for (x,) in S if x > a}))

if __name__ == '__main__':
    main()