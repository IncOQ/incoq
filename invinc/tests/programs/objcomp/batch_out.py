from invinc.runtime import *
N = Set()
for i in range(1, 5):
    N._add(i)
s1 = Set()
s2 = Set()
for i in N:
    o = Obj()
    o.i = i
    if (i % 2):
        s1.add(o)
    else:
        s2.add(o)
s = s1
print(sorted({o.i for o in s}))
s = s2
print(sorted({o.i for o in s}))