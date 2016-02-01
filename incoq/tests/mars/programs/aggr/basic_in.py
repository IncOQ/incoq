# Basic aggregate incrementalization.

from incoq.mars.runtime import *

SYMCONFIG('Q',
    impl = 'inc',
)

S = Set()

def main():
    for x in [1, 2, 3, 4]:
        S.add((x,))
    print(QUERY('Q', count(S)))
    S.remove((4,))
    print(QUERY('Q', count(S)))
#    S.clear()
    print(QUERY('Q', count(S)))

if __name__ == '__main__':
    main()
