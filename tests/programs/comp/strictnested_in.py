# Nested tuple structure and strict update rewriting.

from incoq.runtime import *

CONFIG(
    default_impl = 'inc',
)

S = Set()

def main():
    for x in [1, 2, 3]:
        S.add(((x, x * 10), x * 100))
    print(sorted(QUERY('Q', {(c,) for ((a, b), c) in S})))
    
    S.add(((1, 10), 100))
    print(sorted(QUERY('Q', {(c,) for ((a, b), c) in S})))
    
    S.clear()
    print(sorted(QUERY('Q', {(c,) for ((a, b), c) in S})))

if __name__ == '__main__':
    main()
