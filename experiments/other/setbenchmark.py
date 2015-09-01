from incoq.runtime import Set, RCSet
from time import clock
from random import shuffle
import gc

gc.disable()

N = 1000000
TRIALS = 10

def run(size):
    nums = list(range(size))
    shuffle(nums)
    s = Set()
#    s = RCSet()
#    f = s.add
    
    c1 = clock()
    for n in nums:
        s.add(n)
#        f(n)
#        if n not in s:
#            s.add(n)
#        else:
#            s.incref(n)
    c2 = clock()
    return c2 - c1

results = []
for _ in range(TRIALS):
    t = run(N)
    results.append(t)
    print(format(t, '.3f'))

avg = sum(results) / len(results)
print('-' * 10)
print(format(avg, '.3f'))
