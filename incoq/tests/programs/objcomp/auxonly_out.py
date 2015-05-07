from incoq.runtime import *
def query_Comp1(s):
    's -> {o_i : (s, o) in _M, (o, o_i) in _F_i}'
    result = set()
    if isinstance(s, Set):
        for o in s:
            if hasattr(o, 'i'):
                o_i = o.i
                if (o_i not in result):
                    result.add(o_i)
    return result

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
print(sorted(query_Comp1(s)))
s = s2
print(sorted(query_Comp1(s)))