# Aggregates of object-domain expressions.

from incoq.mars.runtime import *

CONFIG(
    obj_domain = True,
)
SYMCONFIG('Q',
    impl = 'inc',
)

def main():
    p = Obj()
    q = Obj()
    p.f = Set()
    q.f = Set()
    for i in [1, 2, 3, 4]:
        r = p if i % 2 else q
        r.f.add(i)
    
    o = p
    print(QUERY('Q', sum(o.f)))
    o = r
    print(QUERY('Q', sum(o.f)))

if __name__ == '__main__':
    main()
