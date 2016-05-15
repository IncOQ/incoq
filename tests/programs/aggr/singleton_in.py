# Aggregate of a global set that needs singleton wrapping to be a
# relation.

from incoq.runtime import *

CONFIG(
    default_impl = 'inc',
)

S = Set()

def main():
    for x in [1, 2, 3, 4]:
        S.add(x)
    print(QUERY('Q1', count(S)))
    print(QUERY('Q2', sum(S)))
    print(QUERY('Q3', min(S)))
    print(QUERY('Q4', max(S)))

if __name__ == '__main__':
    main()
