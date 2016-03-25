import matplotlib.pyplot as plt
import random
from time import clock
import pubauth_in
import pubauth_inc
import pubauth_dem


A = 10
K = 1000


def run(pubauth, n_pubs, n_auths, k):
    pubs = [None for _ in range(n_pubs)]
    # Init.
    for i in range(n_pubs):
        a = random.randrange(n_auths)
        p = pubauth.make_pub(a)
        pubs[i] = p
    
    t1 = clock()
    for _ in range(k):
        i = random.randrange(n_pubs)
        old_p = pubs[i]
        pubauth.remove_pub(old_p)
        
        a = random.randrange(n_auths)
        new_p = pubauth.make_pub(a)
        pubs[i] = new_p
        
        pubauth.do_query()
    t2 = clock()
    
    pubauth.clear_all()
    
    print('.', end='', flush=True)
    return t2 - t1


xs = list(range(100, 2000 + 1, 100))
y1s = []
y2s = []
y3s = []
for x in xs:
    y1s.append(run(pubauth_in, x, A, K))
    y2s.append(run(pubauth_inc, x, A, K))
    y3s.append(run(pubauth_dem, x, A, K))
    print()

plt.plot(xs, y1s, '-o', label='orig')
plt.plot(xs, y2s, '-o', label='inc')
plt.plot(xs, y3s, '-o', label='dem')
plt.legend()
plt.show()
