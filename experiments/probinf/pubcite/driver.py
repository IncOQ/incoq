import matplotlib.pyplot as plt
import random
from time import clock
import pubcite_in
import pubcite_inc
import pubcite_dem


A = 10
D = 10
K = 1000


def run(pubcite, n_cites, n_auths, n_dates, k):
    cites = [None for _ in range(n_cites)]
    # Init.
    for i in range(n_cites):
        a1 = random.randrange(n_auths)
        d1 = random.randrange(n_dates)
        a2 = random.randrange(n_auths)
        d2 = random.randrange(n_dates)
        c = pubcite.add_cite(a1, d1, a2, d2)
        cites[i] = c
    
    t1 = clock()
    for _ in range(k):
        i = random.randrange(n_cites)
        old_c = cites[i]
        pubcite.remove_cite(old_c)
        
        a1 = random.randrange(n_auths)
        d1 = random.randrange(n_dates)
        a2 = random.randrange(n_auths)
        d2 = random.randrange(n_dates)
        new_c = pubcite.add_cite(a1, d1, a2, d2)
        cites[i] = new_c
        
        pubcite.do_query()
    t2 = clock()
    
    pubcite.clear_all()
    
    print('.', end='', flush=True)
    return t2 - t1


xs = list(range(100, 2000 + 1, 100))
y1s = []
y2s = []
y3s = []
for x in xs:
    y1s.append(run(pubcite_in, x, A, D, K))
    y2s.append(run(pubcite_inc, x, A, D, K))
    y3s.append(run(pubcite_dem, x, A, D, K))
    print()

plt.plot(xs, y1s, '-o', label='orig')
plt.plot(xs, y2s, '-o', label='inc')
plt.plot(xs, y3s, '-o', label='dem')
plt.legend()
plt.show()
