# Nesting a query with a tuple result.

from incoq.runtime import *

CONFIG(
    obj_domain = 'true',
    default_impl = 'inc',
)

def main():
    s = Set()
    for e in [(1, 2), (3, 4)]:
        s.add(e)
    
    print(sorted(QUERY('Q2', {z for z in QUERY('Q1',
                                {(x, y) for (x, y) in s})})))

if __name__ == '__main__':
    main()
