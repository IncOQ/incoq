"""Benchmark a few of the runtimelib types in comparison
with native Python types.
"""


from time import clock
from runtimelib import Set


def run(settype, N, trials):
    s = settype()
    t1 = clock()
    for _ in range(trials):
        for x in range(N):
            s.add(5)
            s.remove(5)
    t2 = clock()
    return (t2 - t1) / trials

native_time = run(set, 300000, 50)
runtimelib_time = run(Set, 300000, 50)
print(format(native_time, '.6f'))
print(format(runtimelib_time, '.6f'))
