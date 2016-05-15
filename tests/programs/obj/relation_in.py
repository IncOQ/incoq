# Object-domain with relations.

from incoq.runtime import *

CONFIG(
    obj_domain = 'true',
    default_impl = 'inc',
)

S = Set()

def main():
    r = Set()
    t = Set()
    for i in [1, 2, 3, 4]:
        if i % 2 == 1:
            r.add(i)
        else:
            t.add(i)
        S.add(i)
    
    z = r
    print(sorted(QUERY('Q', {x for x in z if x in S})))
    z = t
    print(sorted(QUERY('Q', {x for x in z if x in S})))

if __name__ == '__main__':
    main()
