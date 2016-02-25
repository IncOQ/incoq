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
    print(sorted(QUERY('Q', {(x,) for (x,) in S if x > a})))
    for v in [2, 4]:
        S.add((v,))
    print(sorted(QUERY('Q', {(x,) for (x,) in S if x > a})))
    print(sorted(QUERY('Q', {(x,) for (x,) in S if x > a},
                       {'nodemand': True})))

if __name__ == '__main__':
    main()
