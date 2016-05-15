# Global sets of non-tuples that need to be rewritten as relations.

from incoq.mars.runtime import *

CONFIG(
    default_impl = 'inc',
)

S = Set()

def main():
    for a in [1, 2, 3, 4]:
        S.add(a)
    print(sorted(QUERY('Q', {x for x in S if x > 2})))

if __name__ == '__main__':
    main()
