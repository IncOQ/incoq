# Nested object-domain comprehensions.

from incoq.mars.runtime import *

CONFIG(
    obj_domain = 'True',
)
SYMCONFIG('Q1',
    impl = 'inc',
)
SYMCONFIG('Q2',
    impl = 'inc',
)

def main():
    s = Set()
    t = Set()
    for i in [1, 2, 3, 4]:
        p = Obj()
        p.f = i
        r = s if i % 2 else t
        r.add(p)
    
    z = s
    print(sorted(QUERY('Q1', {o.f for o in QUERY('Q2', {m for m in z})})))
    z = t
    print(sorted(QUERY('Q1', {o.f for o in QUERY('Q2', {m for m in z})})))

if __name__ == '__main__':
    main()
