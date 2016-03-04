# Queries with map lookups and nested tuples.

from incoq.mars.runtime import *
from itertools import product

CONFIG(
    obj_domain = True,
)
SYMCONFIG('Q',
    impl = 'filtered',
)

def main():
    a = Map()
    b = Map()
    for (i, j) in product(range(4), range(4)):
        p = Obj()
        p.f = i
        q = Obj()
        q.f = j
        r = a if i % 2 == 0 else b
        if i not in r:
            r[i] = Set()
        r[i].add((p, q))
    p = Obj()
    p.f = 5
    
    m = a
    k = 0
    print(sorted(QUERY('Q', {(x.f, y.f) for (x, y) in m[k]})))
    m = b
    k = 1
    print(sorted(QUERY('Q', {(x.f, y.f) for (x, y) in m[k]})))
    
    del b[1]
    b[1] = Set()
    p = Obj()
    p.f = 100
    q = Obj()
    q.f = 100
    b[1].add((p, q))
    print(sorted(QUERY('Q', {(x.f, y.f) for (x, y) in m[k]})))

if __name__ == '__main__':
    main()
