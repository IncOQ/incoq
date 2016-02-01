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

S = Set()

def main():
    for x in [1, 2, 3, 4]:
        S.add((x,))
    print(QUERY('Q1', count(S)))
    print(QUERY('Q2', sum(S)))
    print(QUERY('Q3', min(S)))
    print(QUERY('Q4', max(S)))
    
    S.remove((4,))
    print(QUERY('Q1', count(S)))
    print(QUERY('Q2', sum(S)))
    print(QUERY('Q3', min(S)))
    print(QUERY('Q4', max(S)))
    
    S.clear()
    print(QUERY('Q1', count(S)))
    print(QUERY('Q2', sum(S)))
    print(QUERY('Q3', min(S)))
    print(QUERY('Q4', max(S)))

if __name__ == '__main__':
    main()
