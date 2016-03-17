from incoq.runtime import *

pubs = set()
p1 = Obj()
p1.author = 'Einstein'
pubs.add(p1)
p2 = Obj()
p2.author = 'Newton'
pubs.add(p2)
p3 = Obj()
p3.author = 'Einstein'
pubs.add(p3)

print(count({p for p in pubs if p.author == 'Einstein'}))

pubs.remove(p3)
print(count({p for p in pubs if p.author == 'Einstein'}))
