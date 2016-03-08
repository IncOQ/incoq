# Filtering in the object-domain.

from incoq.mars.runtime import *

CONFIG(
    obj_domain = 'true',
    default_impl = 'filtered',
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
    print(sorted(QUERY('Q', {o.f for o in z})))
    z = t
    print(sorted(QUERY('Q', {o.f for o in z})))

if __name__ == '__main__':
    main()
