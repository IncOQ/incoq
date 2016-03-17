from incoq.runtime import *
from osq import query

s = Set()

def do_query():
    return set(query('s -> {o.f for o in s}', s))

o1 = Obj()
o1.f = 1
o2 = Obj()
o2.f = 2

o3 = Obj()

s.add(o1)
print(do_query())
s.add(o2)
o1.f = 11
print(do_query())
#s.add(3)
#s.add(o3)
