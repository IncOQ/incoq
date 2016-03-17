from incoq.runtime import *

citations = Set()

c1 = Obj()
c1.source = Obj()
c1.source.author = 'Einstein'
c1.source.date = 1905
c1.target = Obj()
c1.target.author = 'Galileo'
c1.target.date = 1632

c2 = Obj()
c2.source = Obj()
c2.source.author = 'Einstein'
c2.source.date = 1905
c2.target = Obj()
c2.target.author = 'Newton'
c2.target.date = 1684

c3 = Obj()
c3.source = Obj()
c3.source.author = 'Einstein'
c3.source.date = 1915
c3.target = Obj()
c3.target.author = 'Galileo'
c3.target.date = 1590

citations.add(c1)
citations.add(c2)
citations.add(c3)

print(count({c for c in citations if c.source.author == 'Einstein'
               if c.target.author == 'Galileo'}))

citations.remove(c1)

print(count({c for c in citations if c.source.author == 'Einstein'
               if c.target.author == 'Galileo'}))
