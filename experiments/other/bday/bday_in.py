from incoq.runtime import *

bdays = set()
bdays.update([1, 2, 3])
BREL = set()
BREL.update([('jon', 1), ('bo', 1), ('annie', 2)])

print(count({b for b in bdays if count({p for (p, b2) in BREL if b2 == b}) > 1}))

BREL.remove(('jon', 1))
BREL.add(('jon', 3))

print(count({b for b in bdays if count({p for (p, b2) in BREL if b2 == b}) > 1}))
