# Basic aggregate incrementalization.

from incoq.mars.runtime import *

SYMCONFIG('Q1',
    impl = 'inc',
)
SYMCONFIG('Q2',
    impl = 'inc',
)
SYMCONFIG('Q3',
    impl = 'inc',
)
SYMCONFIG('Q4',
    impl = 'inc',
)
SYMCONFIG('Q5',
    impl = 'inc',
)
SYMCONFIG('Q6',
    impl = 'inc',
)

S = Set()

def main():
    for x in [1, 2, 3, 4]:
        S.add((x,))
    print(QUERY('Q1', count(unwrap(S))))
    print(QUERY('Q2', sum(unwrap(S))))
    print(QUERY('Q3', min(unwrap(S))))
    print(QUERY('Q4', max(unwrap(S))))
    print(QUERY('Q5', min(S)))
    print(QUERY('Q6', max(S)))
    
    S.remove((4,))
    print(QUERY('Q1', count(unwrap(S))))
    print(QUERY('Q2', sum(unwrap(S))))
    print(QUERY('Q3', min(unwrap(S))))
    print(QUERY('Q4', max(unwrap(S))))
    print(QUERY('Q5', min(S)))
    print(QUERY('Q6', max(S)))
    
    S.clear()
    print(QUERY('Q1', count(unwrap(S))))
    print(QUERY('Q2', sum(unwrap(S))))
    print(QUERY('Q3', min(unwrap(S))))
    print(QUERY('Q4', max(unwrap(S))))
    print(QUERY('Q5', min(S)))
    print(QUERY('Q6', max(S)))

if __name__ == '__main__':
    main()
